"""Trial system for A/B testing and evolution"""
from .trial_manager import TrialManager, Trial, TrialBranch, TrialResult

__all__ = ['TrialManager', 'Trial', 'TrialBranch', 'TrialResult']
