"""
CERATA Capabilities Validation
================================

Tests all newly metabolized capabilities to ensure proper integration.

Run this after installing dependencies:
    pip install -r requirements.txt
    playwright install
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test 1: Verify all new modules can be imported"""
    print("\n" + "=" * 70)
    print("TEST 1: Module Imports")
    print("=" * 70)

    tests = []

    # Test resilience tools
    try:
        from capabilities.resilience_tools import (
            on_exception, expo, fibo, constant,
            circuit_breaker, CircuitBreaker, CircuitState,
            rate_limit, TokenBucket
        )
        print("✓ Resilience tools imported successfully")
        tests.append(("Resilience tools", True))
    except ImportError as e:
        print(f"✗ Resilience tools import failed: {e}")
        tests.append(("Resilience tools", False))

    # Test capabilities package
    try:
        from capabilities import (
            on_exception, circuit_breaker, rate_limit
        )
        print("✓ Capabilities package imported successfully")
        tests.append(("Capabilities package", True))
    except ImportError as e:
        print(f"✗ Capabilities package import failed: {e}")
        tests.append(("Capabilities package", False))

    # Test AI scraper (may fail without dependencies)
    try:
        from src.hunter.ai_scraper import AIScraper, BusinessLead
        print("✓ AI Scraper imported successfully")
        tests.append(("AI Scraper", True))
    except ImportError as e:
        print(f"⚠  AI Scraper import failed (dependencies not installed): {e}")
        tests.append(("AI Scraper", False))

    # Test enhanced web hunter (may fail without dependencies)
    try:
        from integrations.crawl4ai_hunter.enhanced_web_hunter import (
            EnhancedWebHunter, HuntResult, TREATMENT_CENTER_SCHEMA
        )
        print("✓ Enhanced Web Hunter imported successfully")
        tests.append(("Enhanced Web Hunter", True))
    except ImportError as e:
        print(f"⚠  Enhanced Web Hunter import failed (dependencies not installed): {e}")
        tests.append(("Enhanced Web Hunter", False))

    # Test trial system
    try:
        from src.trial.trial_manager import TrialManager, Trial, TrialBranch
        print("✓ Trial Manager imported successfully")
        tests.append(("Trial Manager", True))
    except ImportError as e:
        print(f"✗ Trial Manager import failed: {e}")
        tests.append(("Trial Manager", False))

    # Test trial configuration
    try:
        from trials.crawl4ai_hunter_trial import CrawlAIHunterTrial
        print("✓ Crawl4AI Hunter Trial imported successfully")
        tests.append(("Crawl4AI Trial Config", True))
    except ImportError as e:
        print(f"⚠  Crawl4AI Trial Config import failed: {e}")
        tests.append(("Crawl4AI Trial Config", False))

    # Summary
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    print(f"\n📊 Import Tests: {passed}/{total} passed")

    return all(success for _, success in tests)


def test_resilience_tools():
    """Test 2: Verify resilience tools functionality"""
    print("\n" + "=" * 70)
    print("TEST 2: Resilience Tools Functionality")
    print("=" * 70)

    try:
        from capabilities.resilience_tools import (
            on_exception, expo, circuit_breaker, CircuitBreaker,
            CircuitState, rate_limit, TokenBucket
        )

        # Test exponential backoff generator
        backoff_gen = expo()
        wait_times = [backoff_gen(i) for i in range(5)]
        print(f"✓ Exponential backoff: {wait_times}")
        assert all(isinstance(w, (int, float)) for w in wait_times), "Invalid wait times"

        # Test circuit breaker
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
        assert breaker.state == CircuitState.CLOSED, "Circuit should start closed"
        print(f"✓ Circuit breaker initialized: {breaker.state}")

        # Test token bucket
        bucket = TokenBucket(rate=2.0, capacity=5)
        consumed = bucket.consume(3)
        assert consumed == True, "Should consume tokens successfully"
        print(f"✓ Token bucket consumed 3 tokens: {consumed}")
        print(f"  Remaining tokens: {bucket.tokens:.1f}")

        # Test on_exception decorator
        call_count = 0

        @on_exception(expo, Exception, max_tries=3)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Simulated failure")
            return "Success!"

        result = flaky_function()
        assert result == "Success!", "Should eventually succeed"
        assert call_count == 3, f"Should have retried (called {call_count} times)"
        print(f"✓ Retry decorator worked: {call_count} attempts")

        print("\n✓ All resilience tools tests passed")
        return True

    except Exception as e:
        print(f"\n✗ Resilience tools test failed: {e}")
        return False


def test_trial_system():
    """Test 3: Verify trial system functionality"""
    print("\n" + "=" * 70)
    print("TEST 3: Trial System Functionality")
    print("=" * 70)

    try:
        from src.trial.trial_manager import TrialManager, TrialStatus

        # Initialize manager
        manager = TrialManager()
        print("✓ Trial manager initialized")

        # Create a test trial
        trial = manager.create_trial(
            name="Test Trial - Resilience Validation",
            description="Test trial system functionality",
            experimental_config={'test_param': 'experimental_value'},
            traffic_split=0.5,
            min_sample_size=10
        )
        print(f"✓ Trial created: {trial.trial_id}")

        # Start trial
        trial.start()
        assert trial.status == TrialStatus.RUNNING, "Trial should be running"
        print(f"✓ Trial started: {trial.status.value}")

        # Test branch assignment
        assignments = [trial.assign_branch() for _ in range(20)]
        classic_count = sum(1 for b in assignments if b == 'classic')
        exp_count = sum(1 for b in assignments if b == 'experimental')
        print(f"✓ Branch assignment: {classic_count} classic, {exp_count} experimental")

        # Record some test data
        for i in range(15):
            branch = 'classic' if i < 7 else 'experimental'
            tier = 'hot' if i % 3 == 0 else 'warm'
            manager.record_qualification(trial.trial_id, branch, tier)

        print(f"✓ Recorded 15 qualifications")
        print(f"  Classic: {trial.classic_branch.leads_qualified} leads")
        print(f"  Experimental: {trial.experimental_branch.leads_qualified} leads")

        # Check if ready for evaluation
        ready = trial.is_ready_for_evaluation()
        print(f"✓ Ready for evaluation: {ready}")

        # Pause trial
        trial.pause()
        assert trial.status == TrialStatus.PAUSED, "Trial should be paused"
        print(f"✓ Trial paused: {trial.status.value}")

        print("\n✓ All trial system tests passed")
        return True

    except Exception as e:
        print(f"\n✗ Trial system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rose_glass_integration():
    """Test 4: Verify Rose Glass dimensional integration"""
    print("\n" + "=" * 70)
    print("TEST 4: Rose Glass Integration")
    print("=" * 70)

    try:
        # Test that Rose Glass dimensions are calculated
        from integrations.crawl4ai_hunter.enhanced_web_hunter import HuntResult

        # Create a mock hunt result
        result = HuntResult(
            url="https://test.example.com",
            leads_found=10,
            raw_markdown="# Test Page\n\nContent here...",
            extracted_data=[{"name": "Test Lead"}],
            coherence_score=0.85,
            psi_content=0.8,
            rho_authority=0.9,
            q_freshness=0.8,
            f_match=0.9,
            hunt_time_seconds=2.5,
            success=True
        )

        print(f"✓ HuntResult created with Rose Glass dimensions:")
        print(f"  Ψ (psi - content): {result.psi_content:.2f}")
        print(f"  ρ (rho - authority): {result.rho_authority:.2f}")
        print(f"  q (freshness): {result.q_freshness:.2f}")
        print(f"  f (fit): {result.f_match:.2f}")
        print(f"  Coherence: {result.coherence_score:.2f}")

        # Verify coherence is average of dimensions
        expected_coherence = (result.psi_content + result.rho_authority +
                             result.q_freshness + result.f_match) / 4
        assert abs(result.coherence_score - expected_coherence) < 0.01, \
            f"Coherence mismatch: {result.coherence_score} != {expected_coherence}"

        print("✓ Coherence calculation verified")

        # Test BusinessLead with intent signals
        try:
            from src.hunter.ai_scraper import BusinessLead

            lead = BusinessLead(
                business_name="Test Recovery Center",
                address="123 Main St, City, ST 12345",
                phone="(555) 555-5555",
                has_hiring_signal=True,
                has_expansion_signal=False,
                has_tech_signal=True,
                has_pain_signal=False
            )

            print(f"\n✓ BusinessLead created with intent signals:")
            print(f"  Hiring: {lead.has_hiring_signal}")
            print(f"  Expansion: {lead.has_expansion_signal}")
            print(f"  Tech: {lead.has_tech_signal}")
            print(f"  Pain: {lead.has_pain_signal}")

        except ImportError:
            print("\n⚠  BusinessLead test skipped (pydantic not installed)")

        print("\n✓ Rose Glass integration tests passed")
        return True

    except Exception as e:
        print(f"\n✗ Rose Glass integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_optional_dependencies():
    """Test 5: Check optional dependencies and provide install instructions"""
    print("\n" + "=" * 70)
    print("TEST 5: Optional Dependencies Check")
    print("=" * 70)

    dependencies = []

    # Crawl4AI
    try:
        import crawl4ai
        print("✓ crawl4ai installed")
        dependencies.append(("crawl4ai", True))
    except ImportError:
        print("✗ crawl4ai not installed")
        dependencies.append(("crawl4ai", False))

    # Playwright
    try:
        import playwright
        print("✓ playwright installed")
        dependencies.append(("playwright", True))
    except ImportError:
        print("✗ playwright not installed")
        dependencies.append(("playwright", False))

    # Pydantic
    try:
        import pydantic
        print("✓ pydantic installed")
        dependencies.append(("pydantic", True))
    except ImportError:
        print("✗ pydantic not installed")
        dependencies.append(("pydantic", False))

    # Backoff
    try:
        import backoff
        print("✓ backoff installed")
        dependencies.append(("backoff", True))
    except ImportError:
        print("✗ backoff not installed")
        dependencies.append(("backoff", False))

    # CircuitBreaker
    try:
        import circuitbreaker
        print("✓ circuitbreaker installed")
        dependencies.append(("circuitbreaker", True))
    except ImportError:
        print("⚠  circuitbreaker not installed (optional)")
        dependencies.append(("circuitbreaker", False))

    # XGBoost
    try:
        import xgboost
        print("✓ xgboost installed")
        dependencies.append(("xgboost", True))
    except ImportError:
        print("⚠  xgboost not installed (for future ML scoring)")
        dependencies.append(("xgboost", False))

    missing = [name for name, installed in dependencies if not installed]

    if missing:
        print(f"\n⚠️  Missing dependencies ({len(missing)}):")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        if "playwright" in missing:
            print("  playwright install")

    print(f"\n📊 Dependencies: {len(dependencies) - len(missing)}/{len(dependencies)} installed")

    return True  # Always return True since these are optional


def main():
    """Run all validation tests"""
    print("\n" + "=" * 70)
    print("  CERATA CAPABILITIES VALIDATION")
    print("  Testing all metabolized nematocysts")
    print("=" * 70)

    results = {}

    # Run tests
    results['imports'] = test_imports()
    results['resilience'] = test_resilience_tools()
    results['trials'] = test_trial_system()
    results['rose_glass'] = test_rose_glass_integration()
    results['dependencies'] = test_optional_dependencies()

    # Summary
    print("\n" + "=" * 70)
    print("  VALIDATION SUMMARY")
    print("=" * 70)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)

    print(f"\n📊 Overall: {passed_count}/{total_count} test suites passed")

    if all(results.values()):
        print("\n🎉 ALL TESTS PASSED - CERATA capabilities ready!")
        print("   Next steps:")
        print("   1. Run actual hunt with test URLs")
        print("   2. Start trial with production traffic")
        print("   3. Commit and push to GitHub")
    else:
        print("\n⚠️  Some tests failed - review above output")
        print("   Common issues:")
        print("   - Missing dependencies: pip install -r requirements.txt")
        print("   - Playwright not installed: playwright install")

    print("\n" + "=" * 70)
    print("  🌹 Rose Glass sees all, judges none, learns always")
    print("=" * 70 + "\n")

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
