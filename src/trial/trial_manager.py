"""
Trial Manager
=============

CERATA Evolution: "Test everything, promote winners"

Implements A/B testing where experimental approaches compete with
the classic (current standard). Winners become the new standard.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import logging
import json
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrialStatus(Enum):
    """Trial lifecycle states"""
    PLANNED = 'planned'
    RUNNING = 'running'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    PROMOTED = 'promoted'  # Experimental became standard
    ARCHIVED = 'archived'  # Experimental lost


@dataclass
class TrialBranch:
    """
    One branch of a trial (either classic or experimental).

    Tracks its own metrics independently.
    """

    name: str  # 'classic' or 'experimental_X'
    description: str

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)

    # Metrics
    leads_qualified: int = 0
    leads_hot: int = 0
    leads_warm: int = 0
    leads_cold: int = 0
    leads_disqualified: int = 0

    outcomes_won: int = 0
    outcomes_lost: int = 0
    total_revenue: float = 0.0
    total_cost: float = 0.0

    # Derived metrics
    @property
    def qualification_rate(self) -> float:
        """% of leads that weren't disqualified"""
        total = self.leads_qualified
        if total == 0:
            return 0.0
        qualified = total - self.leads_disqualified
        return qualified / total

    @property
    def conversion_rate(self) -> float:
        """% of qualified leads that won"""
        total_outcomes = self.outcomes_won + self.outcomes_lost
        if total_outcomes == 0:
            return 0.0
        return self.outcomes_won / total_outcomes

    @property
    def avg_deal_value(self) -> float:
        """Average revenue per won deal"""
        if self.outcomes_won == 0:
            return 0.0
        return self.total_revenue / self.outcomes_won

    @property
    def roi(self) -> float:
        """Return on investment"""
        if self.total_cost == 0:
            return 0.0
        return (self.total_revenue - self.total_cost) / self.total_cost

    @property
    def fitness_score(self) -> float:
        """
        Overall fitness score for branch selection.

        Formula: qualification_rate * 0.3 + conversion_rate * 0.5 + revenue_weight * 0.2
        """
        # Revenue weight (normalized to 0-1, capped at $100k avg)
        revenue_weight = min(self.avg_deal_value / 100000, 1.0)

        fitness = (
            self.qualification_rate * 0.3 +
            self.conversion_rate * 0.5 +
            revenue_weight * 0.2
        )

        return fitness

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'description': self.description,
            'config': self.config,
            'metrics': {
                'leads_qualified': self.leads_qualified,
                'leads_hot': self.leads_hot,
                'leads_warm': self.leads_warm,
                'leads_cold': self.leads_cold,
                'leads_disqualified': self.leads_disqualified,
                'outcomes_won': self.outcomes_won,
                'outcomes_lost': self.outcomes_lost,
                'total_revenue': round(self.total_revenue, 2),
                'total_cost': round(self.total_cost, 2),
            },
            'derived': {
                'qualification_rate': round(self.qualification_rate, 3),
                'conversion_rate': round(self.conversion_rate, 3),
                'avg_deal_value': round(self.avg_deal_value, 2),
                'roi': round(self.roi, 2),
                'fitness_score': round(self.fitness_score, 3),
            }
        }


@dataclass
class Trial:
    """
    A trial comparing classic approach vs experimental approach.
    """

    trial_id: str
    name: str
    description: str

    # Branches
    classic_branch: TrialBranch
    experimental_branch: TrialBranch

    # Configuration
    traffic_split: float = 0.5  # % of leads to experimental (default 50/50)
    min_sample_size: int = 50  # Minimum leads per branch before evaluation
    confidence_threshold: float = 0.95  # Statistical confidence required

    # Status
    status: TrialStatus = TrialStatus.PLANNED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    winner: Optional[str] = None  # 'classic' or 'experimental'
    confidence: Optional[float] = None

    def start(self):
        """Start the trial"""
        self.status = TrialStatus.RUNNING
        self.started_at = datetime.now()
        logger.info(f"▶️  Trial {self.trial_id} STARTED: {self.name}")

    def pause(self):
        """Pause the trial"""
        self.status = TrialStatus.PAUSED
        logger.info(f"⏸️  Trial {self.trial_id} PAUSED")

    def resume(self):
        """Resume the trial"""
        self.status = TrialStatus.RUNNING
        logger.info(f"▶️  Trial {self.trial_id} RESUMED")

    def is_ready_for_evaluation(self) -> bool:
        """Check if trial has enough data for evaluation"""
        return (
            self.classic_branch.leads_qualified >= self.min_sample_size and
            self.experimental_branch.leads_qualified >= self.min_sample_size
        )

    def assign_branch(self) -> str:
        """Assign an incoming lead to a branch (classic or experimental)"""
        if self.status != TrialStatus.RUNNING:
            return 'classic'  # Default to classic if trial not running

        # Randomized assignment based on traffic_split
        return 'experimental' if random.random() < self.traffic_split else 'classic'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'trial_id': self.trial_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'traffic_split': self.traffic_split,
            'min_sample_size': self.min_sample_size,
            'classic_branch': self.classic_branch.to_dict(),
            'experimental_branch': self.experimental_branch.to_dict(),
            'winner': self.winner,
            'confidence': round(self.confidence, 3) if self.confidence else None,
        }


@dataclass
class TrialResult:
    """Results of trial evaluation"""

    trial_id: str
    winner: str  # 'classic', 'experimental', or 'inconclusive'
    confidence: float  # Statistical confidence (0-1)

    classic_fitness: float
    experimental_fitness: float
    improvement: float  # % improvement of winner over loser

    recommendation: str  # 'promote', 'continue', 'archive'
    rationale: str

    evaluated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'trial_id': self.trial_id,
            'winner': self.winner,
            'confidence': round(self.confidence, 3),
            'classic_fitness': round(self.classic_fitness, 3),
            'experimental_fitness': round(self.experimental_fitness, 3),
            'improvement': round(self.improvement, 2),
            'recommendation': self.recommendation,
            'rationale': self.rationale,
            'evaluated_at': self.evaluated_at.isoformat(),
        }


class TrialManager:
    """
    Manages trials for system evolution.

    CERATA Philosophy:
    - Always run at least one trial (classic vs experimental)
    - Promote winners to become new standard
    - Archive losers but keep learnings
    - Use graveyard nutrients to inspire new experiments
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path(__file__).parent.parent.parent / 'data' / 'trials'
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.trials: List[Trial] = []
        self.standards_history: List[Dict] = []  # History of promoted approaches

        self._load_trials()

        logger.info(f"✓ Trial Manager initialized: {self.storage_dir}")
        logger.info(f"  {len(self.trials)} trials tracked")

    def create_trial(
        self,
        name: str,
        description: str,
        experimental_config: Dict[str, Any],
        traffic_split: float = 0.5,
        min_sample_size: int = 50
    ) -> Trial:
        """
        Create a new trial comparing classic vs experimental approach.

        Args:
            name: Trial name (e.g., "Weighted Lens Experiment")
            description: What's being tested
            experimental_config: Configuration for experimental branch
            traffic_split: % to experimental (default 50/50)
            min_sample_size: Minimum leads before evaluation
        """
        trial_id = f"trial_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create branches
        classic_branch = TrialBranch(
            name='classic',
            description='Current standard approach',
            config=self._get_current_standard()
        )

        experimental_branch = TrialBranch(
            name=f'experimental_{trial_id}',
            description=description,
            config=experimental_config
        )

        trial = Trial(
            trial_id=trial_id,
            name=name,
            description=description,
            classic_branch=classic_branch,
            experimental_branch=experimental_branch,
            traffic_split=traffic_split,
            min_sample_size=min_sample_size,
        )

        self.trials.append(trial)
        self._save_trial(trial)

        logger.info(f"🧪 Created trial: {name} ({trial_id})")
        logger.info(f"  Split: {int((1-traffic_split)*100)}% classic / {int(traffic_split*100)}% experimental")

        return trial

    def record_qualification(
        self,
        trial_id: str,
        branch: str,
        tier: str
    ):
        """Record a lead qualification for a trial branch"""
        trial = self._get_trial(trial_id)
        if not trial:
            return

        branch_obj = self._get_branch(trial, branch)
        if not branch_obj:
            return

        branch_obj.leads_qualified += 1

        if tier == 'hot':
            branch_obj.leads_hot += 1
        elif tier == 'warm':
            branch_obj.leads_warm += 1
        elif tier == 'cold':
            branch_obj.leads_cold += 1
        elif tier == 'disqualified':
            branch_obj.leads_disqualified += 1

        self._save_trial(trial)

    def record_outcome(
        self,
        trial_id: str,
        branch: str,
        outcome_type: str,
        deal_value: float = 0.0,
        cost: float = 0.0
    ):
        """Record a lead outcome for a trial branch"""
        trial = self._get_trial(trial_id)
        if not trial:
            return

        branch_obj = self._get_branch(trial, branch)
        if not branch_obj:
            return

        if outcome_type == 'won':
            branch_obj.outcomes_won += 1
            branch_obj.total_revenue += deal_value
        else:
            branch_obj.outcomes_lost += 1

        branch_obj.total_cost += cost
        self._save_trial(trial)

    def evaluate_trial(self, trial_id: str) -> Optional[TrialResult]:
        """
        Evaluate a trial and determine winner.

        Returns TrialResult with recommendation.
        """
        trial = self._get_trial(trial_id)
        if not trial:
            return None

        if not trial.is_ready_for_evaluation():
            logger.warning(
                f"Trial {trial_id} not ready for evaluation - "
                f"need {trial.min_sample_size} leads per branch"
            )
            return None

        classic_fitness = trial.classic_branch.fitness_score
        experimental_fitness = trial.experimental_branch.fitness_score

        # Determine winner
        if experimental_fitness > classic_fitness * 1.05:  # 5% threshold
            winner = 'experimental'
            improvement = ((experimental_fitness - classic_fitness) / classic_fitness) * 100
            confidence = self._calculate_confidence(trial)
            recommendation = 'promote' if confidence > 0.95 else 'continue'
            rationale = (
                f"Experimental shows {improvement:.1f}% improvement "
                f"(fitness: {experimental_fitness:.3f} vs {classic_fitness:.3f})"
            )

        elif classic_fitness > experimental_fitness * 1.05:
            winner = 'classic'
            improvement = ((classic_fitness - experimental_fitness) / experimental_fitness) * 100
            confidence = self._calculate_confidence(trial)
            recommendation = 'archive'
            rationale = (
                f"Classic performs {improvement:.1f}% better "
                f"(fitness: {classic_fitness:.3f} vs {experimental_fitness:.3f})"
            )

        else:
            winner = 'inconclusive'
            improvement = 0.0
            confidence = 0.0
            recommendation = 'continue'
            rationale = "No significant difference - need more data"

        result = TrialResult(
            trial_id=trial_id,
            winner=winner,
            confidence=confidence,
            classic_fitness=classic_fitness,
            experimental_fitness=experimental_fitness,
            improvement=improvement,
            recommendation=recommendation,
            rationale=rationale,
        )

        trial.winner = winner
        trial.confidence = confidence

        logger.info(f"\n📊 Trial Evaluation: {trial.name}")
        logger.info(f"  Winner: {winner.upper()}")
        logger.info(f"  Confidence: {confidence:.1%}")
        logger.info(f"  Improvement: {improvement:.1f}%")
        logger.info(f"  Recommendation: {recommendation.upper()}")
        logger.info(f"  {rationale}")

        self._save_trial(trial)
        self._save_result(result)

        return result

    def promote_experimental(self, trial_id: str):
        """
        Promote experimental branch to become new standard.

        This is CERATA evolution in action.
        """
        trial = self._get_trial(trial_id)
        if not trial:
            return

        if trial.winner != 'experimental':
            logger.warning(f"Cannot promote - experimental is not the winner")
            return

        # Archive old standard
        old_standard = self._get_current_standard()
        self.standards_history.append({
            'config': old_standard,
            'replaced_at': datetime.now().isoformat(),
            'replaced_by': trial.experimental_branch.name,
            'trial_id': trial_id,
        })

        # Promote experimental to standard
        new_standard = trial.experimental_branch.config
        self._save_standard(new_standard)

        trial.status = TrialStatus.PROMOTED
        self._save_trial(trial)

        logger.info(f"🚀 PROMOTED: {trial.experimental_branch.name} → NEW STANDARD")
        logger.info(f"  Trial: {trial.name}")
        logger.info(f"  Fitness improvement: {trial.winner} won with {trial.confidence:.1%} confidence")

    def archive_trial(self, trial_id: str):
        """Archive a trial (experimental lost)"""
        trial = self._get_trial(trial_id)
        if not trial:
            return

        trial.status = TrialStatus.ARCHIVED
        trial.completed_at = datetime.now()
        self._save_trial(trial)

        logger.info(f"📦 ARCHIVED: Trial {trial.name}")

    def get_active_trial(self) -> Optional[Trial]:
        """Get currently running trial"""
        for trial in self.trials:
            if trial.status == TrialStatus.RUNNING:
                return trial
        return None

    def _get_trial(self, trial_id: str) -> Optional[Trial]:
        """Find trial by ID"""
        for trial in self.trials:
            if trial.trial_id == trial_id:
                return trial
        return None

    def _get_branch(self, trial: Trial, branch_name: str) -> Optional[TrialBranch]:
        """Get branch from trial"""
        if 'classic' in branch_name.lower():
            return trial.classic_branch
        else:
            return trial.experimental_branch

    def _calculate_confidence(self, trial: Trial) -> float:
        """
        Calculate statistical confidence in result.

        Simplified - production would use proper statistical tests
        (e.g., chi-square for conversion rates).
        """
        # Simplified confidence based on sample size and difference
        classic_n = trial.classic_branch.leads_qualified
        exp_n = trial.experimental_branch.leads_qualified

        # Larger samples = higher confidence
        sample_confidence = min((classic_n + exp_n) / (trial.min_sample_size * 4), 1.0)

        # Larger difference = higher confidence
        fitness_diff = abs(
            trial.classic_branch.fitness_score -
            trial.experimental_branch.fitness_score
        )
        difference_confidence = min(fitness_diff / 0.2, 1.0)  # 20% difference = full confidence

        return (sample_confidence + difference_confidence) / 2

    def _get_current_standard(self) -> Dict[str, Any]:
        """Get current standard configuration"""
        standards_file = self.storage_dir / 'current_standard.json'
        if standards_file.exists():
            with open(standards_file, 'r') as f:
                return json.load(f)

        # Default standard
        return {
            'lens': 'enterprise_saas',
            'weights': {
                'psi_intent': 0.25,
                'rho_authority': 0.30,
                'q_urgency': 0.25,
                'f_fit': 0.20,
            },
            'approach': 'classic_rose_glass'
        }

    def _save_standard(self, config: Dict[str, Any]):
        """Save new standard configuration"""
        standards_file = self.storage_dir / 'current_standard.json'
        with open(standards_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _save_trial(self, trial: Trial):
        """Save trial to storage"""
        filepath = self.storage_dir / f"{trial.trial_id}.json"
        with open(filepath, 'w') as f:
            json.dump(trial.to_dict(), f, indent=2)

    def _save_result(self, result: TrialResult):
        """Save trial result"""
        results_dir = self.storage_dir / 'results'
        results_dir.mkdir(exist_ok=True)

        filepath = results_dir / f"{result.trial_id}_result.json"
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)

    def _load_trials(self):
        """Load existing trials from storage"""
        if not self.storage_dir.exists():
            return

        for filepath in self.storage_dir.glob('trial_*.json'):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    # Reconstruct trial object (simplified - production would be more robust)
                    # For now, just log that trials exist
                    logger.info(f"  Found trial: {data.get('name')}")
            except Exception as e:
                logger.warning(f"Failed to load {filepath}: {e}")


# Example usage
if __name__ == "__main__":
    manager = TrialManager()

    print("\n" + "=" * 60)
    print("ROSE GLASS CRM - Trial System Demo")
    print("=" * 60)

    # Create experimental trial
    trial = manager.create_trial(
        name="Authority-Weighted Lens",
        description="Test increasing ρ (authority) weight to 0.40 from 0.30",
        experimental_config={
            'lens': 'enterprise_saas',
            'weights': {
                'psi_intent': 0.20,
                'rho_authority': 0.40,  # Increased from 0.30
                'q_urgency': 0.20,
                'f_fit': 0.20,
            },
            'approach': 'authority_weighted'
        },
        traffic_split=0.5,
        min_sample_size=50
    )

    trial.start()

    # Simulate qualifications
    print("\n📊 Simulating lead qualifications...")
    for i in range(60):
        branch = trial.assign_branch()
        tier = random.choices(
            ['hot', 'warm', 'cold', 'disqualified'],
            weights=[0.15, 0.35, 0.30, 0.20]
        )[0]
        manager.record_qualification(trial.trial_id, branch, tier)

    # Simulate outcomes
    print("📊 Simulating outcomes...")
    for i in range(30):
        branch = 'classic' if i < 15 else 'experimental'
        outcome = random.choices(['won', 'lost'], weights=[0.3, 0.7])[0]
        deal_value = random.randint(20000, 80000) if outcome == 'won' else 0
        manager.record_outcome(trial.trial_id, branch, outcome, deal_value, cost=5000)

    # Evaluate trial
    print("\n" + "=" * 60)
    result = manager.evaluate_trial(trial.trial_id)

    if result and result.recommendation == 'promote':
        print("\n🚀 Promoting experimental to standard...")
        manager.promote_experimental(trial.trial_id)
