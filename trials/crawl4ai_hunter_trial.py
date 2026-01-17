"""
CERATA Trial: Crawl4AI Enhanced Hunter
========================================

Compare Crawl4AI-powered async hunter vs classic requests-based hunter.

Trial Metrics:
- Speed: Pages crawled per minute
- Accuracy: Lead extraction completeness (% of expected fields found)
- Stealth: Success rate avoiding detection
- Richness: Average data fields per lead

CERATA Evolution: "Test everything, promote winners"
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
import logging
import time
from datetime import datetime

# Trial Manager
import sys
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from trial.trial_manager import TrialManager

# Hunters
sys.path.append(str(Path(__file__).parent.parent))
from integrations.crawl4ai_hunter.enhanced_web_hunter import (
    EnhancedWebHunter,
    TREATMENT_CENTER_SCHEMA
)
from src.hunter.ai_scraper import AIScraper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CrawlAIHunterTrial:
    """
    Trial configuration for Crawl4AI enhanced hunting.

    Compares two approaches:
    - Classic: Traditional requests-based scraping
    - Experimental: Async Crawl4AI with LLM fallback

    Success Criteria:
    - 15%+ improvement in speed (pages/min)
    - 10%+ improvement in extraction accuracy
    - Equal or better stealth effectiveness
    """

    def __init__(self):
        self.trial_manager = TrialManager()
        self.trial = None

    def create_trial(self) -> str:
        """
        Create and configure the Crawl4AI hunter trial.

        Returns:
            trial_id for tracking
        """
        # Classic configuration (current approach)
        classic_config = {
            'hunter': 'classic_web_hunter',
            'approach': 'requests_based',
            'features': {
                'async': False,
                'stealth_mode': False,
                'llm_extraction': False,
                'css_extraction': True,
                'dynamic_content': False,
            },
            'extraction_strategy': 'css_only',
            'max_concurrent': 1,
            'expected_speed_ppm': 5,  # pages per minute
        }

        # Experimental configuration (Crawl4AI)
        experimental_config = {
            'hunter': 'crawl4ai_enhanced',
            'approach': 'async_crawl4ai',
            'features': {
                'async': True,
                'stealth_mode': True,
                'llm_extraction': True,  # Fallback
                'css_extraction': True,  # Primary
                'dynamic_content': True,  # Wait for networkidle
            },
            'extraction_strategy': 'hybrid',  # CSS + LLM fallback
            'browser_config': {
                'headless': True,
                'stealth_mode': True,
            },
            'llm_provider': 'openai/gpt-4o-mini',
            'max_concurrent': 5,
            'expected_speed_ppm': 50,  # 10x improvement target
        }

        self.trial = self.trial_manager.create_trial(
            name="Crawl4AI Enhanced Hunting",
            description=(
                "Test Crawl4AI async crawler with LLM extraction vs "
                "classic requests-based scraping. Measures speed, accuracy, "
                "stealth, and data richness."
            ),
            experimental_config=experimental_config,
            traffic_split=0.5,  # 50/50 split
            min_sample_size=50,  # Minimum 50 URLs per branch
        )

        logger.info(f"\n🧪 Created Crawl4AI Hunter Trial: {self.trial.trial_id}")
        logger.info(f"  Classic: {classic_config['approach']}")
        logger.info(f"  Experimental: {experimental_config['approach']}")
        logger.info(f"  Split: 50/50")
        logger.info(f"  Min sample: 50 URLs per branch")

        return self.trial.trial_id

    async def run_hunt_comparison(
        self,
        test_urls: List[str],
        extraction_schema: Dict[str, Any] = None
    ):
        """
        Run a hunt comparison between classic and experimental.

        Args:
            test_urls: URLs to scrape
            extraction_schema: CSS schema for extraction
        """
        if not self.trial:
            raise ValueError("Trial not created - call create_trial() first")

        schema = extraction_schema or TREATMENT_CENTER_SCHEMA

        logger.info(f"\n🔍 Running hunt comparison on {len(test_urls)} URLs...")

        # Initialize hunters
        enhanced_hunter = EnhancedWebHunter(
            headless=True,
            stealth_mode=True
        )

        # For classic, we'd use the existing WebHunter
        # For now, we'll simulate classic results

        # Run experimental hunt
        logger.info("\n▶️  EXPERIMENTAL: Crawl4AI Enhanced Hunter")
        exp_start = time.time()

        try:
            exp_results = await enhanced_hunter.hunt_leads(
                urls=test_urls,
                extraction_schema=schema,
                use_llm=False  # CSS first, LLM fallback if needed
            )

            exp_duration = time.time() - exp_start
            exp_leads_found = sum(r.leads_found for r in exp_results)
            exp_success_rate = sum(1 for r in exp_results if r.success) / len(exp_results)
            exp_avg_coherence = sum(r.coherence_score for r in exp_results) / len(exp_results)

            logger.info(f"  ✓ Experimental complete:")
            logger.info(f"    Duration: {exp_duration:.2f}s")
            logger.info(f"    Leads found: {exp_leads_found}")
            logger.info(f"    Success rate: {exp_success_rate:.1%}")
            logger.info(f"    Avg coherence: {exp_avg_coherence:.2f}")
            logger.info(f"    Speed: {len(test_urls) / (exp_duration / 60):.1f} pages/min")

            # Record to trial
            for result in exp_results:
                # Map hunt results to trial metrics
                if result.success:
                    # Tier based on coherence score
                    if result.coherence_score >= 0.8:
                        tier = 'hot'
                    elif result.coherence_score >= 0.6:
                        tier = 'warm'
                    elif result.coherence_score >= 0.4:
                        tier = 'cold'
                    else:
                        tier = 'disqualified'

                    self.trial_manager.record_qualification(
                        self.trial.trial_id,
                        'experimental',
                        tier
                    )

                    # Record outcome (success = won)
                    self.trial_manager.record_outcome(
                        self.trial.trial_id,
                        'experimental',
                        outcome_type='won' if result.success else 'lost',
                        deal_value=result.leads_found * 100,  # Value per lead
                        cost=0  # No LLM cost if CSS only
                    )

        except Exception as e:
            logger.error(f"  ❌ Experimental hunt failed: {e}")

        # For classic comparison, we'd run the same URLs through classic hunter
        # Simulating classic results for now:
        logger.info("\n▶️  CLASSIC: Traditional Web Hunter")
        logger.info("  (Simulated results - integrate actual classic hunter)")

        # Simulate classic being slower but similar accuracy
        classic_duration = exp_duration * 5  # 5x slower
        classic_leads = int(exp_leads_found * 0.9)  # 90% as accurate
        classic_success_rate = exp_success_rate * 0.8  # 80% success (less stealth)

        logger.info(f"  ✓ Classic complete:")
        logger.info(f"    Duration: {classic_duration:.2f}s (simulated)")
        logger.info(f"    Leads found: {classic_leads} (simulated)")
        logger.info(f"    Success rate: {classic_success_rate:.1%} (simulated)")
        logger.info(f"    Speed: {len(test_urls) / (classic_duration / 60):.1f} pages/min")

    def evaluate(self) -> str:
        """
        Evaluate trial and get recommendation.

        Returns:
            Recommendation: 'promote', 'continue', or 'archive'
        """
        if not self.trial:
            raise ValueError("Trial not created")

        result = self.trial_manager.evaluate_trial(self.trial.trial_id)

        if not result:
            return 'continue'

        logger.info(f"\n📊 TRIAL EVALUATION COMPLETE")
        logger.info(f"  Winner: {result.winner}")
        logger.info(f"  Confidence: {result.confidence:.1%}")
        logger.info(f"  Improvement: {result.improvement:.1f}%")
        logger.info(f"  Recommendation: {result.recommendation.upper()}")
        logger.info(f"  Rationale: {result.rationale}")

        return result.recommendation

    def promote(self):
        """Promote experimental to standard (if it won)"""
        if not self.trial:
            raise ValueError("Trial not created")

        self.trial_manager.promote_experimental(self.trial.trial_id)

        logger.info(f"\n🚀 PROMOTED: Crawl4AI Enhanced Hunter → NEW STANDARD")
        logger.info(f"  Classic hunter archived")
        logger.info(f"  Enhanced hunter now default for web hunting")


async def demo_trial():
    """
    Demo the Crawl4AI hunter trial.

    Tests with sample URLs to demonstrate trial system.
    """
    print("\n" + "=" * 70)
    print("  CERATA TRIAL: Crawl4AI Enhanced Hunter")
    print("=" * 70)

    trial = CrawlAIHunterTrial()

    # Create trial
    trial_id = trial.create_trial()

    # Start trial
    trial.trial.start()

    # Test URLs (replace with actual targets)
    test_urls = [
        "https://example.com/treatment-centers?page=1",
        "https://example.com/treatment-centers?page=2",
        "https://example.com/treatment-centers?page=3",
    ]

    print("\n🧪 Running hunt comparison...")
    print(f"  Testing {len(test_urls)} URLs")

    # Run comparison
    await trial.run_hunt_comparison(test_urls)

    # Evaluate
    print("\n📊 Evaluating trial...")
    recommendation = trial.evaluate()

    if recommendation == 'promote':
        print("\n🎯 Experimental hunter outperformed classic!")
        print("  Ready to promote to production")
        # trial.promote()  # Uncomment to actually promote
    elif recommendation == 'continue':
        print("\n⏳ Need more data - continue trial")
    else:
        print("\n📦 Classic won - experimental archived")

    print("\n" + "=" * 70)
    print("  🌹 Rose Glass sees all, judges none, learns always")
    print("=" * 70 + "\n")


# Example usage for integration
def integrate_with_web_hunter():
    """
    Example: How to integrate trial with existing web hunter.

    In your main hunting code:
    """
    example_code = '''
    from trials.crawl4ai_hunter_trial import CrawlAIHunterTrial

    # Initialize trial
    trial = CrawlAIHunterTrial()
    trial_id = trial.create_trial()
    trial.trial.start()

    # In your hunt loop:
    for url in urls_to_scrape:
        # Assign to branch
        branch = trial.trial.assign_branch()

        if branch == 'experimental':
            # Use Crawl4AI enhanced hunter
            results = await enhanced_hunter.hunt_leads([url], schema)
        else:
            # Use classic hunter
            results = classic_hunter.scrape([url])

        # Record results
        # ... (see run_hunt_comparison for example)

    # After min_sample_size reached:
    recommendation = trial.evaluate()

    if recommendation == 'promote':
        trial.promote()  # Crawl4AI becomes standard!
    '''

    print("Integration Example:")
    print(example_code)


if __name__ == "__main__":
    # Check dependencies
    try:
        from integrations.crawl4ai_hunter.enhanced_web_hunter import EnhancedWebHunter

        # Run demo
        asyncio.run(demo_trial())

    except ImportError as e:
        print(f"\n⚠️  Dependencies not installed:")
        print(f"   {e}")
        print(f"\nInstall with:")
        print(f"   pip install crawl4ai playwright pydantic")
        print(f"   playwright install")
        print(f"\nThen run: python trials/crawl4ai_hunter_trial.py")
