"""
Outcome Recorder
================

Records final outcomes of leads and extracts learnings.
Feeds nutrients to graveyard for system evolution.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging
import json
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutcomeType(Enum):
    """Final outcome categories"""
    WON = 'won'                    # Became customer
    LOST_TO_COMPETITOR = 'lost_competitor'  # Chose competitor
    LOST_NO_BUDGET = 'lost_no_budget'      # Budget constraints
    LOST_NO_DECISION = 'lost_no_decision'  # No decision made
    LOST_TIMING = 'lost_timing'           # Wrong timing
    LOST_DARK = 'lost_dark'               # Went dark
    DISQUALIFIED = 'disqualified'          # Never qualified
    NURTURE_ONGOING = 'nurture_ongoing'    # Still in nurture


@dataclass
class Outcome:
    """Record of a lead's final outcome"""

    # Identity
    lead_id: str
    company_name: str
    outcome_type: OutcomeType

    # Financial impact
    deal_value: float = 0.0          # Revenue (if won)
    expected_value: float = 0.0      # Original estimated value
    cost_to_acquire: float = 0.0     # Sales/marketing costs

    # Timeline
    created_at: datetime = field(default_factory=datetime.now)
    first_contact_at: Optional[datetime] = None
    qualified_at: Optional[datetime] = None
    outcome_at: datetime = field(default_factory=datetime.now)

    # Journey metadata
    qualification_tier: Optional[str] = None  # 'hot', 'warm', 'cold'
    coherence_score: Optional[float] = None
    trial_branch: Optional[str] = None

    # Learnings (nutrients for graveyard)
    loss_reason: Optional[str] = None
    competitor_chosen: Optional[str] = None
    what_went_wrong: List[str] = field(default_factory=list)
    what_went_right: List[str] = field(default_factory=list)
    lesson_learned: Optional[str] = None

    # Notes
    notes: str = ''

    def __post_init__(self):
        """Calculate derived metrics"""
        if isinstance(self.outcome_type, str):
            self.outcome_type = OutcomeType(self.outcome_type)

    @property
    def is_won(self) -> bool:
        return self.outcome_type == OutcomeType.WON

    @property
    def is_lost(self) -> bool:
        return self.outcome_type.value.startswith('lost_')

    @property
    def is_disqualified(self) -> bool:
        return self.outcome_type == OutcomeType.DISQUALIFIED

    @property
    def days_to_close(self) -> Optional[int]:
        """Days from first contact to outcome"""
        if self.first_contact_at:
            delta = self.outcome_at - self.first_contact_at
            return delta.days
        return None

    @property
    def roi(self) -> float:
        """Return on investment"""
        if self.cost_to_acquire > 0:
            return (self.deal_value - self.cost_to_acquire) / self.cost_to_acquire
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'lead_id': self.lead_id,
            'company_name': self.company_name,
            'outcome_type': self.outcome_type.value,
            'is_won': self.is_won,
            'is_lost': self.is_lost,
            'deal_value': round(self.deal_value, 2),
            'expected_value': round(self.expected_value, 2),
            'cost_to_acquire': round(self.cost_to_acquire, 2),
            'roi': round(self.roi, 2),
            'days_to_close': self.days_to_close,
            'outcome_at': self.outcome_at.isoformat(),
            'qualification_tier': self.qualification_tier,
            'coherence_score': round(self.coherence_score, 3) if self.coherence_score else None,
            'trial_branch': self.trial_branch,
            'loss_reason': self.loss_reason,
            'competitor_chosen': self.competitor_chosen,
            'learnings': {
                'what_went_wrong': self.what_went_wrong,
                'what_went_right': self.what_went_right,
                'lesson_learned': self.lesson_learned,
            },
            'notes': self.notes,
        }


class OutcomeRecorder:
    """
    Records and analyzes lead outcomes.

    Responsibilities:
    1. Record final outcomes with metadata
    2. Extract learnings (nutrients) for graveyard
    3. Calculate conversion metrics
    4. Feed trial system for evolution
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).parent.parent.parent / 'data' / 'outcomes'
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.outcomes = []  # In-memory cache
        self._load_outcomes()

        logger.info(f"✓ Outcome Recorder initialized: {self.storage_dir}")

    def record_won(
        self,
        lead_id: str,
        company_name: str,
        deal_value: float,
        qualification_tier: Optional[str] = None,
        coherence_score: Optional[float] = None,
        trial_branch: Optional[str] = None,
        what_went_right: Optional[List[str]] = None,
        **kwargs
    ) -> Outcome:
        """Record a won deal (became customer)"""
        outcome = Outcome(
            lead_id=lead_id,
            company_name=company_name,
            outcome_type=OutcomeType.WON,
            deal_value=deal_value,
            qualification_tier=qualification_tier,
            coherence_score=coherence_score,
            trial_branch=trial_branch,
            what_went_right=what_went_right or [],
            **kwargs
        )

        self._save_outcome(outcome)
        logger.info(
            f"🎉 WON: {company_name} - ${deal_value:,.0f} "
            f"({qualification_tier or 'unknown'} → {outcome.days_to_close}d)"
        )

        return outcome

    def record_lost(
        self,
        lead_id: str,
        company_name: str,
        loss_type: OutcomeType,
        expected_value: float = 0.0,
        qualification_tier: Optional[str] = None,
        coherence_score: Optional[float] = None,
        trial_branch: Optional[str] = None,
        loss_reason: Optional[str] = None,
        competitor_chosen: Optional[str] = None,
        what_went_wrong: Optional[List[str]] = None,
        lesson_learned: Optional[str] = None,
        **kwargs
    ) -> Outcome:
        """Record a lost deal"""
        outcome = Outcome(
            lead_id=lead_id,
            company_name=company_name,
            outcome_type=loss_type,
            expected_value=expected_value,
            qualification_tier=qualification_tier,
            coherence_score=coherence_score,
            trial_branch=trial_branch,
            loss_reason=loss_reason,
            competitor_chosen=competitor_chosen,
            what_went_wrong=what_went_wrong or [],
            lesson_learned=lesson_learned,
            **kwargs
        )

        self._save_outcome(outcome)
        logger.info(
            f"❌ LOST ({loss_type.value}): {company_name} - "
            f"{qualification_tier or 'unknown'} tier "
            f"({outcome.days_to_close}d)"
        )

        if competitor_chosen:
            logger.info(f"  → Lost to: {competitor_chosen}")
        if loss_reason:
            logger.info(f"  → Reason: {loss_reason}")

        return outcome

    def record_disqualified(
        self,
        lead_id: str,
        company_name: str,
        coherence_score: Optional[float] = None,
        what_went_wrong: Optional[List[str]] = None,
        **kwargs
    ) -> Outcome:
        """Record a disqualified lead"""
        outcome = Outcome(
            lead_id=lead_id,
            company_name=company_name,
            outcome_type=OutcomeType.DISQUALIFIED,
            qualification_tier='disqualified',
            coherence_score=coherence_score,
            what_went_wrong=what_went_wrong or [],
            **kwargs
        )

        self._save_outcome(outcome)
        logger.info(f"⛔ DISQUALIFIED: {company_name} (C={coherence_score:.2f})")

        return outcome

    def _save_outcome(self, outcome: Outcome):
        """Save outcome to storage"""
        self.outcomes.append(outcome)

        # Save to JSON file
        filename = f"{outcome.lead_id}_{outcome.outcome_type.value}.json"
        filepath = self.storage_dir / filename

        with open(filepath, 'w') as f:
            json.dump(outcome.to_dict(), f, indent=2)

    def _load_outcomes(self):
        """Load existing outcomes from storage"""
        if not self.storage_dir.exists():
            return

        for filepath in self.storage_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Reconstruct Outcome object
                    outcome = Outcome(**{
                        k: v for k, v in data.items()
                        if k not in ['is_won', 'is_lost', 'roi', 'days_to_close', 'learnings']
                    })
                    self.outcomes.append(outcome)
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")

        logger.info(f"  Loaded {len(self.outcomes)} historical outcomes")

    def get_conversion_metrics(self, trial_branch: Optional[str] = None) -> Dict[str, Any]:
        """Calculate conversion and revenue metrics"""
        outcomes = self.outcomes
        if trial_branch:
            outcomes = [o for o in outcomes if o.trial_branch == trial_branch]

        if not outcomes:
            return {'error': 'No outcomes recorded'}

        total = len(outcomes)
        won = [o for o in outcomes if o.is_won]
        lost = [o for o in outcomes if o.is_lost]
        disqualified = [o for o in outcomes if o.is_disqualified]

        # By qualification tier
        by_tier = {}
        for tier in ['hot', 'warm', 'cold', 'disqualified']:
            tier_outcomes = [o for o in outcomes if o.qualification_tier == tier]
            tier_won = [o for o in tier_outcomes if o.is_won]
            by_tier[tier] = {
                'total': len(tier_outcomes),
                'won': len(tier_won),
                'conversion_rate': len(tier_won) / len(tier_outcomes) if tier_outcomes else 0,
            }

        # Financial
        total_revenue = sum(o.deal_value for o in won)
        total_cost = sum(o.cost_to_acquire for o in outcomes if o.cost_to_acquire > 0)
        avg_deal_size = total_revenue / len(won) if won else 0

        # Timeline
        days_to_close = [o.days_to_close for o in won if o.days_to_close]
        avg_days_to_close = sum(days_to_close) / len(days_to_close) if days_to_close else 0

        return {
            'total_outcomes': total,
            'won': len(won),
            'lost': len(lost),
            'disqualified': len(disqualified),
            'conversion_rate': len(won) / total if total > 0 else 0,
            'by_tier': by_tier,
            'revenue': {
                'total': round(total_revenue, 2),
                'avg_deal_size': round(avg_deal_size, 2),
                'total_cost': round(total_cost, 2),
                'roi': round((total_revenue - total_cost) / total_cost if total_cost > 0 else 0, 2),
            },
            'timeline': {
                'avg_days_to_close': round(avg_days_to_close, 1),
                'fastest_deal': min(days_to_close) if days_to_close else None,
                'slowest_deal': max(days_to_close) if days_to_close else None,
            },
            'trial_branch': trial_branch,
        }

    def get_graveyard_nutrients(self) -> List[Dict[str, Any]]:
        """
        Extract learnings (nutrients) from losses and disqualifications.

        These feed the graveyard system for evolution.
        """
        nutrients = []

        lost_and_disqualified = [
            o for o in self.outcomes
            if o.is_lost or o.is_disqualified
        ]

        for outcome in lost_and_disqualified:
            nutrients.append({
                'lead_id': outcome.lead_id,
                'company_name': outcome.company_name,
                'outcome_type': outcome.outcome_type.value,
                'qualification_tier': outcome.qualification_tier,
                'coherence_score': outcome.coherence_score,
                'trial_branch': outcome.trial_branch,
                'what_went_wrong': outcome.what_went_wrong,
                'lesson_learned': outcome.lesson_learned,
                'loss_reason': outcome.loss_reason,
                'competitor_chosen': outcome.competitor_chosen,
            })

        return nutrients

    def export_for_trials(self, filepath: Path, trial_branch: str):
        """Export outcomes for trial analysis"""
        metrics = self.get_conversion_metrics(trial_branch=trial_branch)
        nutrients = self.get_graveyard_nutrients()

        with open(filepath, 'w') as f:
            json.dump({
                'trial_branch': trial_branch,
                'metrics': metrics,
                'nutrients': nutrients,
                'outcomes': [o.to_dict() for o in self.outcomes if o.trial_branch == trial_branch],
            }, f, indent=2)

        logger.info(f"✓ Exported trial outcomes: {filepath}")


# Example usage
if __name__ == "__main__":
    recorder = OutcomeRecorder()

    print("\n" + "=" * 60)
    print("ROSE GLASS CRM - Outcome Recording Demo")
    print("=" * 60)

    # Won deal
    recorder.record_won(
        lead_id='hot001',
        company_name='Acme Enterprise',
        deal_value=50000,
        qualification_tier='hot',
        coherence_score=3.2,
        trial_branch='classic',
        first_contact_at=datetime(2026, 1, 1),
        what_went_right=['Strong authority signals', 'Clear pain point match', 'Fast decision timeline'],
    )

    # Lost to competitor
    recorder.record_lost(
        lead_id='warm002',
        company_name='Beta Corp',
        loss_type=OutcomeType.LOST_TO_COMPETITOR,
        expected_value=30000,
        qualification_tier='warm',
        coherence_score=2.1,
        trial_branch='classic',
        first_contact_at=datetime(2026, 1, 5),
        competitor_chosen='Competitor X',
        loss_reason='Price sensitivity - competitor was 20% cheaper',
        what_went_wrong=['Did not establish value early enough', 'Lost on price, not features'],
        lesson_learned='Mid-market segment is highly price-sensitive - need ROI calculator',
    )

    # Lost - went dark
    recorder.record_lost(
        lead_id='warm003',
        company_name='Gamma LLC',
        loss_type=OutcomeType.LOST_DARK,
        expected_value=25000,
        qualification_tier='warm',
        coherence_score=1.8,
        trial_branch='classic',
        first_contact_at=datetime(2026, 1, 10),
        loss_reason='Contact stopped responding after demo',
        what_went_wrong=['Unclear next steps after demo', 'Did not multi-thread to other stakeholders'],
        lesson_learned='Always establish multi-threaded relationships',
    )

    # Disqualified
    recorder.record_disqualified(
        lead_id='disq001',
        company_name='Delta Consulting',
        coherence_score=0.4,
        what_went_wrong=['Poor ICP fit', 'No decision authority'],
    )

    # Get metrics
    print("\n" + "=" * 60)
    print("CONVERSION METRICS")
    print("=" * 60)

    metrics = recorder.get_conversion_metrics(trial_branch='classic')
    print(json.dumps(metrics, indent=2))

    # Get nutrients for graveyard
    print("\n" + "=" * 60)
    print("GRAVEYARD NUTRIENTS (Learnings)")
    print("=" * 60)

    nutrients = recorder.get_graveyard_nutrients()
    for nutrient in nutrients:
        print(f"\n{nutrient['company_name']} ({nutrient['outcome_type']}):")
        if nutrient['lesson_learned']:
            print(f"  Lesson: {nutrient['lesson_learned']}")
        if nutrient['what_went_wrong']:
            print(f"  Issues: {', '.join(nutrient['what_went_wrong'][:2])}")
