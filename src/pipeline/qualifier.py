"""
Lead Qualifier
==============

Applies Rose Glass perception to qualify leads.
Routes leads based on coherence scores and signals detected.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
import json

# Import core components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.rose_glass_lens import RoseGlassCRMLens, LeadData, LeadCoherence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QualificationResult:
    """Result of qualifying a lead through Rose Glass"""

    lead_id: str
    company_name: str

    # Rose Glass perception
    coherence: LeadCoherence

    # Qualification decision
    qualification_tier: str  # 'hot', 'warm', 'cold', 'disqualified'
    qualified: bool  # True if tier != 'disqualified'

    # Routing
    next_stage: str  # 'active_sales', 'nurture_warm', 'nurture_cold', 'graveyard'
    priority_score: float  # 0-1, for prioritizing hot leads

    # Metadata
    qualified_at: datetime = field(default_factory=datetime.now)
    qualified_by: str = 'rose_glass_auto'
    lens_used: str = 'enterprise_saas'

    # Trial tracking
    trial_branch: Optional[str] = None  # 'classic' or 'experimental_X'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'lead_id': self.lead_id,
            'company_name': self.company_name,
            'qualification_tier': self.qualification_tier,
            'qualified': self.qualified,
            'next_stage': self.next_stage,
            'priority_score': round(self.priority_score, 3),
            'coherence': self.coherence.to_dict(),
            'qualified_at': self.qualified_at.isoformat(),
            'qualified_by': self.qualified_by,
            'lens_used': self.lens_used,
            'trial_branch': self.trial_branch,
        }


class LeadQualifier:
    """
    Qualifies leads using Rose Glass perception.

    Workflow:
    1. Raw lead enters (from hunter or manual)
    2. Rose Glass perceives dimensions (Ψ, ρ, q, f)
    3. Coherence score calculated
    4. Qualification tier assigned
    5. Routing decision made
    6. Result logged for trial system
    """

    def __init__(self, lens_name: str = 'enterprise_saas', trial_branch: Optional[str] = None):
        self.lens = RoseGlassCRMLens(lens_name=lens_name)
        self.lens_name = lens_name
        self.trial_branch = trial_branch or 'classic'

        self.qualification_log = []
        self.stats = {
            'total_qualified': 0,
            'hot': 0,
            'warm': 0,
            'cold': 0,
            'disqualified': 0,
        }

        logger.info(f"✓ Lead Qualifier initialized: lens={lens_name}, branch={self.trial_branch}")

    def qualify(self, lead: LeadData) -> QualificationResult:
        """
        Qualify a single lead through Rose Glass.

        Returns QualificationResult with routing decision.
        """
        logger.info(f"🔍 Qualifying: {lead.company_name} (ID: {lead.lead_id})")

        # Perceive through Rose Glass
        coherence = self.lens.perceive(lead)

        # Determine routing
        next_stage = self._determine_routing(coherence)
        priority_score = self._calculate_priority(coherence)
        qualified = coherence.qualification_tier != 'disqualified'

        result = QualificationResult(
            lead_id=lead.lead_id,
            company_name=lead.company_name,
            coherence=coherence,
            qualification_tier=coherence.qualification_tier,
            qualified=qualified,
            next_stage=next_stage,
            priority_score=priority_score,
            lens_used=self.lens_name,
            trial_branch=self.trial_branch,
        )

        # Update stats
        self._update_stats(result)

        # Log for trial system
        self.qualification_log.append(result.to_dict())

        # Log decision
        logger.info(
            f"  → {result.qualification_tier.upper()}: "
            f"C={coherence.coherence_score:.2f} "
            f"(Ψ={coherence.psi_intent:.2f}, ρ={coherence.rho_authority:.2f}, "
            f"q={coherence.q_urgency:.2f}, f={coherence.f_fit:.2f}) "
            f"→ {result.next_stage}"
        )

        if coherence.positive_signals:
            logger.info(f"  ✓ Signals: {', '.join(coherence.positive_signals[:3])}")
        if coherence.warning_signals:
            logger.info(f"  ⚠️  Warnings: {', '.join(coherence.warning_signals[:2])}")
        if coherence.disqualifiers:
            logger.info(f"  ❌ Disqualifiers: {', '.join(coherence.disqualifiers)}")

        return result

    def qualify_batch(self, leads: List[LeadData]) -> List[QualificationResult]:
        """
        Qualify multiple leads.

        Returns sorted results (hot first, then warm, cold, disqualified).
        """
        logger.info(f"📋 Batch qualification: {len(leads)} leads")

        results = []
        for lead in leads:
            try:
                result = self.qualify(lead)
                results.append(result)
            except Exception as e:
                logger.error(f"  Failed to qualify {lead.company_name}: {e}")

        # Sort by priority
        results.sort(key=lambda r: r.priority_score, reverse=True)

        # Summary
        logger.info(f"\n📊 Batch Summary:")
        logger.info(f"  HOT: {self.stats['hot']} ({self.stats['hot']/len(leads)*100:.1f}%)")
        logger.info(f"  WARM: {self.stats['warm']} ({self.stats['warm']/len(leads)*100:.1f}%)")
        logger.info(f"  COLD: {self.stats['cold']} ({self.stats['cold']/len(leads)*100:.1f}%)")
        logger.info(f"  DISQUALIFIED: {self.stats['disqualified']} ({self.stats['disqualified']/len(leads)*100:.1f}%)")

        return results

    def _determine_routing(self, coherence: LeadCoherence) -> str:
        """Determine next stage based on qualification tier"""
        tier = coherence.qualification_tier

        if tier == 'hot':
            return 'active_sales'
        elif tier == 'warm':
            return 'nurture_warm'
        elif tier == 'cold':
            return 'nurture_cold'
        else:  # disqualified
            return 'graveyard'

    def _calculate_priority(self, coherence: LeadCoherence) -> float:
        """
        Calculate priority score for lead routing.

        Hot leads with high urgency get highest priority.
        """
        base_priority = {
            'hot': 1.0,
            'warm': 0.6,
            'cold': 0.3,
            'disqualified': 0.0,
        }.get(coherence.qualification_tier, 0.0)

        # Boost priority based on urgency and authority
        urgency_boost = coherence.q_urgency * 0.2
        authority_boost = coherence.rho_authority * 0.15

        priority = min(1.0, base_priority + urgency_boost + authority_boost)
        return priority

    def _update_stats(self, result: QualificationResult):
        """Update qualification statistics"""
        self.stats['total_qualified'] += 1
        self.stats[result.qualification_tier] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get qualification statistics"""
        total = self.stats['total_qualified']
        if total == 0:
            return self.stats

        return {
            **self.stats,
            'qualification_rate': (total - self.stats['disqualified']) / total if total > 0 else 0,
            'hot_rate': self.stats['hot'] / total if total > 0 else 0,
            'lens_used': self.lens_name,
            'trial_branch': self.trial_branch,
        }

    def export_log(self, filepath: Path):
        """Export qualification log to JSON (for trial analysis)"""
        with open(filepath, 'w') as f:
            json.dump({
                'stats': self.get_stats(),
                'qualifications': self.qualification_log,
            }, f, indent=2)

        logger.info(f"✓ Exported qualification log: {filepath}")


# Example usage
if __name__ == "__main__":
    from core.rose_glass_lens import LeadData

    # Create qualifier
    qualifier = LeadQualifier(lens_name='enterprise_saas', trial_branch='classic')

    # Example leads
    leads = [
        # Hot lead
        LeadData(
            lead_id='hot001',
            company_name='Acme Enterprise',
            contact_name='John Smith',
            contact_title='VP Engineering',
            contact_email='john@acme.com',
            industry='SaaS',
            company_size='enterprise',
            source='referral',
            pain_points=['security compliance', 'access management', 'audit requirements'],
            is_decision_maker=True,
            budget_mentioned=True,
            timeline_mentioned='this_quarter',
            meeting_requests=2,
            use_case='Replace legacy IAM system',
        ),
        # Warm lead
        LeadData(
            lead_id='warm001',
            company_name='Beta Corp',
            contact_name='Jane Doe',
            contact_title='IT Manager',
            industry='Fintech',
            company_size='mid-market',
            source='inbound',
            pain_points=['user management'],
            timeline_mentioned='next_quarter',
            website_visits=3,
        ),
        # Cold lead
        LeadData(
            lead_id='cold001',
            company_name='Gamma LLC',
            contact_name='Bob Wilson',
            contact_title='Engineer',
            industry='Technology',
            company_size='smb',
            source='outbound',
            website_visits=1,
        ),
        # Disqualified lead
        LeadData(
            lead_id='disq001',
            company_name='Delta Consulting',
            industry='Other',
            company_size='startup',
            source='unknown',
        ),
    ]

    # Batch qualification
    print("\n" + "=" * 60)
    print("ROSE GLASS CRM - Lead Qualification Demo")
    print("=" * 60)

    results = qualifier.qualify_batch(leads)

    print("\n" + "=" * 60)
    print("PRIORITIZED LEADS")
    print("=" * 60)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.company_name} [{result.qualification_tier.upper()}]")
        print(f"   Priority: {result.priority_score:.2f}")
        print(f"   Next Stage: {result.next_stage}")
        print(f"   Top Actions: {', '.join(result.coherence.next_actions[:2])}")

    # Export log
    log_path = Path('/tmp/qualification_log.json')
    qualifier.export_log(log_path)
    print(f"\n✓ Log exported to {log_path}")
