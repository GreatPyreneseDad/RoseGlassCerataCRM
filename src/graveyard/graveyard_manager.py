"""
Graveyard Manager
=================

CERATA Principle: "Failures are nutrients, not waste"

The graveyard is where lost/disqualified leads rest and decompose into
learnings that feed system evolution. Every failure contains knowledge.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Counter
from datetime import datetime
from pathlib import Path
from collections import Counter
import logging
import json
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Nutrient:
    """
    A learning extracted from a failed lead (graveyard nutrient).

    Nutrients are categorized and feed back into system evolution.
    """

    # Source
    lead_id: str
    company_name: str
    outcome_type: str  # 'lost_competitor', 'lost_dark', 'disqualified', etc.

    # Lesson
    category: str  # 'qualification', 'messaging', 'timing', 'authority', 'pricing'
    lesson: str  # The actual learning
    severity: str  # 'minor', 'moderate', 'critical'

    # Context
    qualification_tier: Optional[str] = None
    coherence_score: Optional[float] = None
    trial_branch: Optional[str] = None

    # Metadata
    extracted_at: datetime = field(default_factory=datetime.now)
    applied_to_standard: bool = False  # Has this nutrient been incorporated into standards?

    def to_dict(self) -> Dict[str, Any]:
        return {
            'lead_id': self.lead_id,
            'company_name': self.company_name,
            'outcome_type': self.outcome_type,
            'category': self.category,
            'lesson': self.lesson,
            'severity': self.severity,
            'qualification_tier': self.qualification_tier,
            'coherence_score': round(self.coherence_score, 3) if self.coherence_score else None,
            'trial_branch': self.trial_branch,
            'extracted_at': self.extracted_at.isoformat(),
            'applied_to_standard': self.applied_to_standard,
        }


@dataclass
class FailurePattern:
    """
    Pattern detected across multiple failures.

    Patterns indicate systematic issues that need addressing.
    """

    pattern_type: str  # What kind of pattern
    frequency: int  # How often it occurs
    affected_leads: List[str]  # Which leads showed this pattern

    # Impact
    avg_coherence_at_fail: float
    primary_tier: str  # Which tier shows this pattern most

    # Recommendation
    recommended_action: str
    priority: str  # 'low', 'medium', 'high', 'critical'

    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'pattern_type': self.pattern_type,
            'frequency': self.frequency,
            'affected_leads': self.affected_leads,
            'avg_coherence_at_fail': round(self.avg_coherence_at_fail, 3),
            'primary_tier': self.primary_tier,
            'recommended_action': self.recommended_action,
            'priority': self.priority,
            'detected_at': self.detected_at.isoformat(),
        }


class GraveyardManager:
    """
    Manages the lead graveyard and extracts nutrients from failures.

    CERATA Philosophy:
    - Every failure is an opportunity to learn
    - Patterns in failures reveal system weaknesses
    - Nutrients from graveyard feed trial system evolution
    - Nothing is truly "lost" - all data has value
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).parent.parent.parent / 'data' / 'graveyard'
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.nutrients = []  # Extracted learnings
        self.patterns = []  # Detected patterns
        self.graveyard_leads = []  # All failed leads

        self._load_graveyard()

        logger.info(f"✓ Graveyard Manager initialized: {self.storage_dir}")
        logger.info(f"  {len(self.graveyard_leads)} leads in graveyard")
        logger.info(f"  {len(self.nutrients)} nutrients extracted")

    def bury_lead(self, outcome: Dict[str, Any]) -> List[Nutrient]:
        """
        Bury a failed lead and extract nutrients.

        Args:
            outcome: Outcome dict from OutcomeRecorder

        Returns:
            List of nutrients extracted
        """
        self.graveyard_leads.append(outcome)
        self._save_to_graveyard(outcome)

        # Extract nutrients
        nutrients = self._extract_nutrients(outcome)
        self.nutrients.extend(nutrients)

        logger.info(
            f"⚰️  Buried: {outcome['company_name']} ({outcome['outcome_type']}) "
            f"→ {len(nutrients)} nutrients extracted"
        )

        # Save nutrients
        for nutrient in nutrients:
            self._save_nutrient(nutrient)

        return nutrients

    def _extract_nutrients(self, outcome: Dict[str, Any]) -> List[Nutrient]:
        """Extract learnings (nutrients) from a failed outcome"""
        nutrients = []

        lead_id = outcome['lead_id']
        company_name = outcome['company_name']
        outcome_type = outcome['outcome_type']

        learnings = outcome.get('learnings', {})
        what_went_wrong = learnings.get('what_went_wrong', [])
        lesson_learned = learnings.get('lesson_learned')

        # Extract nutrients from explicit learnings
        for issue in what_went_wrong:
            category = self._categorize_issue(issue)
            severity = self._assess_severity(issue, outcome)

            nutrient = Nutrient(
                lead_id=lead_id,
                company_name=company_name,
                outcome_type=outcome_type,
                category=category,
                lesson=issue,
                severity=severity,
                qualification_tier=outcome.get('qualification_tier'),
                coherence_score=outcome.get('coherence_score'),
                trial_branch=outcome.get('trial_branch'),
            )
            nutrients.append(nutrient)

        # Extract nutrient from overall lesson
        if lesson_learned:
            category = self._categorize_issue(lesson_learned)
            nutrient = Nutrient(
                lead_id=lead_id,
                company_name=company_name,
                outcome_type=outcome_type,
                category=category,
                lesson=lesson_learned,
                severity='moderate',
                qualification_tier=outcome.get('qualification_tier'),
                coherence_score=outcome.get('coherence_score'),
                trial_branch=outcome.get('trial_branch'),
            )
            nutrients.append(nutrient)

        # Infer nutrients from outcome type
        if outcome_type == 'lost_competitor':
            competitor = outcome.get('competitor_chosen')
            if competitor:
                nutrient = Nutrient(
                    lead_id=lead_id,
                    company_name=company_name,
                    outcome_type=outcome_type,
                    category='competitive',
                    lesson=f"Lost to {competitor} - analyze competitive positioning",
                    severity='moderate',
                    qualification_tier=outcome.get('qualification_tier'),
                    coherence_score=outcome.get('coherence_score'),
                    trial_branch=outcome.get('trial_branch'),
                )
                nutrients.append(nutrient)

        elif outcome_type == 'lost_dark':
            nutrient = Nutrient(
                lead_id=lead_id,
                company_name=company_name,
                outcome_type=outcome_type,
                category='engagement',
                lesson="Lead went dark - review engagement cadence and value delivery",
                severity='moderate',
                qualification_tier=outcome.get('qualification_tier'),
                coherence_score=outcome.get('coherence_score'),
                trial_branch=outcome.get('trial_branch'),
            )
            nutrients.append(nutrient)

        elif outcome_type == 'disqualified':
            nutrient = Nutrient(
                lead_id=lead_id,
                company_name=company_name,
                outcome_type=outcome_type,
                category='qualification',
                lesson=f"Disqualified with coherence {outcome.get('coherence_score', 0):.2f} - review qualification criteria",
                severity='minor',
                qualification_tier='disqualified',
                coherence_score=outcome.get('coherence_score'),
                trial_branch=outcome.get('trial_branch'),
            )
            nutrients.append(nutrient)

        return nutrients

    def _categorize_issue(self, issue: str) -> str:
        """Categorize an issue into nutrient category"""
        issue_lower = issue.lower()

        # Category keywords
        categories = {
            'qualification': ['qualify', 'icp', 'fit', 'criteria', 'disqualif'],
            'messaging': ['message', 'value', 'positioning', 'communication', 'pitch'],
            'timing': ['timing', 'timeline', 'urgency', 'too early', 'too late'],
            'authority': ['authority', 'decision', 'stakeholder', 'champion', 'multi-thread'],
            'pricing': ['price', 'budget', 'cost', 'expensive', 'roi'],
            'competitive': ['competitor', 'competitive', 'alternative', 'comparison'],
            'engagement': ['engagement', 'response', 'dark', 'ghosted', 'follow-up'],
            'technical': ['technical', 'integration', 'feature', 'requirement'],
        }

        for category, keywords in categories.items():
            if any(kw in issue_lower for kw in keywords):
                return category

        return 'general'

    def _assess_severity(self, issue: str, outcome: Dict[str, Any]) -> str:
        """Assess severity of an issue"""
        # High-value deals that were lost are critical learnings
        expected_value = outcome.get('expected_value', 0)
        coherence = outcome.get('coherence_score', 0)

        if expected_value > 50000:
            return 'critical'
        elif coherence > 2.5:  # Lost a hot lead
            return 'critical'
        elif coherence > 1.5:  # Lost a warm lead
            return 'moderate'
        else:
            return 'minor'

    def analyze_patterns(self) -> List[FailurePattern]:
        """
        Analyze graveyard to detect patterns across failures.

        Identifies systematic issues that need addressing.
        """
        logger.info(f"🔍 Analyzing graveyard patterns across {len(self.graveyard_leads)} leads...")

        patterns = []

        # Pattern 1: Frequent loss to specific competitor
        competitors = [
            outcome.get('competitor_chosen')
            for outcome in self.graveyard_leads
            if outcome.get('competitor_chosen')
        ]
        if competitors:
            competitor_counts = Counter(competitors)
            for competitor, count in competitor_counts.most_common(3):
                if count >= 2:
                    affected = [
                        o['lead_id'] for o in self.graveyard_leads
                        if o.get('competitor_chosen') == competitor
                    ]
                    pattern = FailurePattern(
                        pattern_type=f"frequent_loss_to_{competitor.replace(' ', '_')}",
                        frequency=count,
                        affected_leads=affected,
                        avg_coherence_at_fail=self._avg_coherence(affected),
                        primary_tier=self._primary_tier(affected),
                        recommended_action=f"Conduct competitive analysis vs {competitor}. Create battle card.",
                        priority='high' if count > 3 else 'medium',
                    )
                    patterns.append(pattern)

        # Pattern 2: Leads going dark at specific tier
        dark_leads = [o for o in self.graveyard_leads if o.get('outcome_type') == 'lost_dark']
        if len(dark_leads) >= 3:
            tier_counts = Counter([o.get('qualification_tier') for o in dark_leads])
            for tier, count in tier_counts.items():
                if count >= 2:
                    affected = [o['lead_id'] for o in dark_leads if o.get('qualification_tier') == tier]
                    pattern = FailurePattern(
                        pattern_type=f"{tier}_tier_going_dark",
                        frequency=count,
                        affected_leads=affected,
                        avg_coherence_at_fail=self._avg_coherence(affected),
                        primary_tier=tier,
                        recommended_action=f"Review engagement strategy for {tier} leads. May need different cadence/content.",
                        priority='high' if tier == 'hot' else 'medium',
                    )
                    patterns.append(pattern)

        # Pattern 3: Consistent disqualification at low coherence
        disqualified = [o for o in self.graveyard_leads if o.get('outcome_type') == 'disqualified']
        if len(disqualified) >= 5:
            avg_c = sum(o.get('coherence_score', 0) for o in disqualified) / len(disqualified)
            if avg_c < 0.8:
                pattern = FailurePattern(
                    pattern_type="weak_qualification_criteria",
                    frequency=len(disqualified),
                    affected_leads=[o['lead_id'] for o in disqualified],
                    avg_coherence_at_fail=avg_c,
                    primary_tier='disqualified',
                    recommended_action="Review hunting criteria. May be targeting wrong ICP.",
                    priority='critical',
                )
                patterns.append(pattern)

        # Pattern 4: Nutrient category frequency
        nutrient_categories = Counter([n.category for n in self.nutrients])
        for category, count in nutrient_categories.most_common(3):
            if count >= 3:
                affected = [
                    n.lead_id for n in self.nutrients
                    if n.category == category
                ]
                pattern = FailurePattern(
                    pattern_type=f"recurring_{category}_issues",
                    frequency=count,
                    affected_leads=list(set(affected)),
                    avg_coherence_at_fail=self._avg_coherence_nutrients(category),
                    primary_tier=self._primary_tier(affected),
                    recommended_action=f"Systematic {category} issues detected. Review {category} processes.",
                    priority='high' if count > 5 else 'medium',
                )
                patterns.append(pattern)

        self.patterns = patterns

        logger.info(f"✓ Detected {len(patterns)} patterns")
        for pattern in patterns:
            logger.info(f"  {pattern.priority.upper()}: {pattern.pattern_type} (n={pattern.frequency})")

        return patterns

    def _avg_coherence(self, lead_ids: List[str]) -> float:
        """Calculate average coherence for given lead IDs"""
        scores = [
            o.get('coherence_score', 0)
            for o in self.graveyard_leads
            if o['lead_id'] in lead_ids and o.get('coherence_score')
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def _avg_coherence_nutrients(self, category: str) -> float:
        """Average coherence for nutrients in a category"""
        scores = [
            n.coherence_score
            for n in self.nutrients
            if n.category == category and n.coherence_score
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def _primary_tier(self, lead_ids: List[str]) -> str:
        """Find most common qualification tier for given leads"""
        tiers = [
            o.get('qualification_tier')
            for o in self.graveyard_leads
            if o['lead_id'] in lead_ids and o.get('qualification_tier')
        ]
        if not tiers:
            return 'unknown'
        return Counter(tiers).most_common(1)[0][0]

    def get_nutrients_by_category(self) -> Dict[str, List[Nutrient]]:
        """Group nutrients by category"""
        by_category = {}
        for nutrient in self.nutrients:
            category = nutrient.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(nutrient)
        return by_category

    def get_critical_nutrients(self) -> List[Nutrient]:
        """Get high-severity nutrients that need immediate attention"""
        return [n for n in self.nutrients if n.severity == 'critical' and not n.applied_to_standard]

    def mark_nutrient_applied(self, nutrient_id: str):
        """Mark a nutrient as applied to standards (incorporated into system)"""
        # In real implementation, would have nutrient IDs
        for nutrient in self.nutrients:
            if nutrient.lead_id == nutrient_id:
                nutrient.applied_to_standard = True

    def _save_to_graveyard(self, outcome: Dict[str, Any]):
        """Save outcome to graveyard storage"""
        filename = f"{outcome['lead_id']}_{outcome['outcome_type']}.json"
        filepath = self.storage_dir / filename

        with open(filepath, 'w') as f:
            json.dump(outcome, f, indent=2)

    def _save_nutrient(self, nutrient: Nutrient):
        """Save extracted nutrient"""
        nutrients_dir = self.storage_dir / 'nutrients'
        nutrients_dir.mkdir(exist_ok=True)

        filename = f"{nutrient.lead_id}_{nutrient.category}_{hashlib.md5(nutrient.lesson.encode()).hexdigest()[:8]}.json"
        filepath = nutrients_dir / filename

        with open(filepath, 'w') as f:
            json.dump(nutrient.to_dict(), f, indent=2)

    def _load_graveyard(self):
        """Load existing graveyard data"""
        if not self.storage_dir.exists():
            return

        # Load outcomes
        for filepath in self.storage_dir.glob('*.json'):
            try:
                with open(filepath, 'r') as f:
                    outcome = json.load(f)
                    self.graveyard_leads.append(outcome)
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")

        # Load nutrients
        nutrients_dir = self.storage_dir / 'nutrients'
        if nutrients_dir.exists():
            for filepath in nutrients_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        nutrient = Nutrient(**{k: v for k, v in data.items() if k != 'extracted_at'})
                        self.nutrients.append(nutrient)
                except Exception as e:
                    logger.warning(f"Failed to load nutrient {filepath}: {e}")

    def export_insights(self, filepath: Path):
        """Export graveyard insights for trial system"""
        patterns = self.analyze_patterns()

        insights = {
            'graveyard_stats': {
                'total_leads': len(self.graveyard_leads),
                'total_nutrients': len(self.nutrients),
                'critical_nutrients': len(self.get_critical_nutrients()),
                'patterns_detected': len(patterns),
            },
            'nutrients_by_category': {
                category: len(nutrients)
                for category, nutrients in self.get_nutrients_by_category().items()
            },
            'patterns': [p.to_dict() for p in patterns],
            'critical_nutrients': [n.to_dict() for n in self.get_critical_nutrients()],
        }

        with open(filepath, 'w') as f:
            json.dump(insights, f, indent=2)

        logger.info(f"✓ Exported graveyard insights: {filepath}")


# Example usage
if __name__ == "__main__":
    graveyard = GraveyardManager()

    print("\n" + "=" * 60)
    print("ROSE GLASS CRM - Graveyard System Demo")
    print("=" * 60)

    # Simulate burying failed leads
    outcomes = [
        {
            'lead_id': 'lost001',
            'company_name': 'Acme Corp',
            'outcome_type': 'lost_competitor',
            'qualification_tier': 'hot',
            'coherence_score': 3.1,
            'trial_branch': 'classic',
            'expected_value': 50000,
            'competitor_chosen': 'Competitor X',
            'learnings': {
                'what_went_wrong': ['Did not multi-thread to other stakeholders', 'Lost on price'],
                'lesson_learned': 'Need better competitive pricing strategy'
            }
        },
        {
            'lead_id': 'lost002',
            'company_name': 'Beta Inc',
            'outcome_type': 'lost_dark',
            'qualification_tier': 'warm',
            'coherence_score': 2.1,
            'trial_branch': 'classic',
            'expected_value': 30000,
            'learnings': {
                'what_went_wrong': ['Unclear next steps after demo'],
                'lesson_learned': 'Always establish clear next steps'
            }
        },
    ]

    for outcome in outcomes:
        nutrients = graveyard.bury_lead(outcome)
        print(f"\nBuried {outcome['company_name']}: {len(nutrients)} nutrients")

    # Analyze patterns
    print("\n" + "=" * 60)
    print("PATTERN ANALYSIS")
    print("=" * 60)

    patterns = graveyard.analyze_patterns()
    for pattern in patterns:
        print(f"\n{pattern.priority.upper()}: {pattern.pattern_type}")
        print(f"  Frequency: {pattern.frequency}")
        print(f"  Action: {pattern.recommended_action}")

    # Critical nutrients
    print("\n" + "=" * 60)
    print("CRITICAL NUTRIENTS (Need Immediate Attention)")
    print("=" * 60)

    critical = graveyard.get_critical_nutrients()
    for nutrient in critical:
        print(f"\n{nutrient.category.upper()}: {nutrient.lesson}")
        print(f"  From: {nutrient.company_name} (C={nutrient.coherence_score:.2f})")
