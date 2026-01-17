#!/usr/bin/env python3
"""
Rose Glass Cerata CRM - System Demo
====================================

Demonstrates the complete system workflow:
1. Lead hunting (manual creation)
2. Rose Glass perception
3. Qualification pipeline
4. Outcome recording
5. Graveyard learning
6. Trial evolution

Run this to validate the system is working correctly.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.rose_glass_lens import RoseGlassCRMLens, LeadData
from hunter.data_hunter import DataHunter
from pipeline.qualifier import LeadQualifier
from pipeline.outcome import OutcomeRecorder, OutcomeType
from graveyard.graveyard_manager import GraveyardManager
from trial.trial_manager import TrialManager


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def demo_rose_glass_perception():
    """Demo: Core Rose Glass perception"""
    print_section("1. ROSE GLASS PERCEPTION - Dimensional Analysis")

    # Create test leads with different profiles
    leads = [
        LeadData(
            lead_id='hot001',
            company_name='Acme Enterprise',
            contact_name='Sarah Chen',
            contact_title='VP of Engineering',
            contact_email='sarah@acme.com',
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
        LeadData(
            lead_id='warm001',
            company_name='Beta Corp',
            contact_name='Mike Johnson',
            contact_title='IT Manager',
            contact_email='mike@beta.com',
            industry='Fintech',
            company_size='mid-market',
            source='inbound',
            pain_points=['user management'],
            timeline_mentioned='next_quarter',
            website_visits=3,
        ),
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
    ]

    lens = RoseGlassCRMLens(lens_name='enterprise_saas')

    for lead in leads:
        coherence = lens.perceive(lead)
        print(f"\n{lead.company_name} ({lead.contact_title}):")
        print(f"  Coherence: {coherence.coherence_score:.2f} / 4.0")
        print(f"  Dimensions:")
        print(f"    Ψ (intent)   = {coherence.psi_intent:.2f}")
        print(f"    ρ (authority) = {coherence.rho_authority:.2f}")
        print(f"    q (urgency)   = {coherence.q_urgency:.2f}")
        print(f"    f (fit)       = {coherence.f_fit:.2f}")
        print(f"  Tier: {coherence.qualification_tier.upper()}")

        if coherence.positive_signals:
            print(f"  ✓ Signals: {', '.join(coherence.positive_signals[:2])}")
        if coherence.warning_signals:
            print(f"  ⚠️  Warnings: {', '.join(coherence.warning_signals[:2])}")

    return leads


def demo_hunter_engines():
    """Demo: Lead hunting and ingestion"""
    print_section("2. HUNTER ENGINES - Lead Discovery")

    hunter = DataHunter()

    # Manual lead creation (simulating form entry)
    print("\n📝 Manual Lead Entry:")
    manual_lead = hunter.create_manual_lead(
        company_name="Delta Industries",
        contact_name="Alice Smith",
        contact_title="CTO",
        contact_email="alice@delta.com",
        industry="Healthcare Tech",
        company_size="enterprise",
        pain_points=["HIPAA compliance", "data encryption"],
        notes="Met at HealthTech Summit 2026 - very interested"
    )
    print(f"  Created: {manual_lead.company_name} ({manual_lead.lead_id})")
    print(f"  Pain points: {', '.join(manual_lead.pain_points)}")

    # Dictionary ingestion (simulating API webhook)
    print("\n📥 Dictionary Ingestion (API/Form):")
    data = [
        {
            'company_name': 'Epsilon Corp',
            'contact_name': 'Tom Davis',
            'email': 'tom@epsilon.com',
            'title': 'Director of IT',
            'industry': 'Manufacturing',
            'pain_points': 'access control, compliance',
        },
    ]
    ingested_leads = hunter.ingest_dict(data, source='web_form')
    print(f"  Ingested {len(ingested_leads)} leads from web form")
    for lead in ingested_leads:
        print(f"    - {lead.company_name} ({lead.industry})")

    return [manual_lead] + ingested_leads


def demo_qualification_pipeline(leads):
    """Demo: Lead qualification through Rose Glass"""
    print_section("3. QUALIFICATION PIPELINE - Rose Glass Analysis")

    qualifier = LeadQualifier(lens_name='enterprise_saas', trial_branch='classic')

    print("\n🔍 Batch Qualification:")
    results = qualifier.qualify_batch(leads)

    print("\n📊 Prioritized Results:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. {result.company_name} [{result.qualification_tier.upper()}]")
        print(f"     Priority: {result.priority_score:.2f} | Next: {result.next_stage}")
        print(f"     Actions: {', '.join(result.coherence.next_actions[:2])}")

    # Stats
    stats = qualifier.get_stats()
    print(f"\n📈 Qualification Stats:")
    print(f"  Total Qualified: {stats['total_qualified']}")
    print(f"  Hot: {stats['hot']} | Warm: {stats['warm']} | Cold: {stats['cold']} | Disqualified: {stats['disqualified']}")
    print(f"  Qualification Rate: {stats['qualification_rate']:.1%}")

    return results


def demo_outcome_recording(results):
    """Demo: Recording outcomes and extracting learnings"""
    print_section("4. OUTCOME RECORDING - Wins & Losses")

    recorder = OutcomeRecorder()

    # Simulate outcomes
    print("\n🎉 Won Deal:")
    if results and results[0].qualification_tier == 'hot':
        recorder.record_won(
            lead_id=results[0].lead_id,
            company_name=results[0].company_name,
            deal_value=60000,
            qualification_tier=results[0].qualification_tier,
            coherence_score=results[0].coherence.coherence_score,
            trial_branch='classic',
            first_contact_at=datetime.now() - timedelta(days=14),
            what_went_right=['Strong authority signals', 'Clear ROI demonstrated', 'Multi-threaded engagement'],
        )

    print("\n❌ Lost Deal (to competitor):")
    if len(results) > 1:
        recorder.record_lost(
            lead_id=results[1].lead_id,
            company_name=results[1].company_name,
            loss_type=OutcomeType.LOST_TO_COMPETITOR,
            expected_value=40000,
            qualification_tier=results[1].qualification_tier,
            coherence_score=results[1].coherence.coherence_score,
            trial_branch='classic',
            first_contact_at=datetime.now() - timedelta(days=21),
            competitor_chosen='Competitor X',
            loss_reason='Price sensitivity - competitor 20% cheaper',
            what_went_wrong=['Did not establish value early', 'Lost on price vs features'],
            lesson_learned='Mid-market needs stronger ROI positioning',
        )

    # Get metrics
    print("\n📊 Conversion Metrics:")
    metrics = recorder.get_conversion_metrics(trial_branch='classic')
    print(f"  Total Outcomes: {metrics['total_outcomes']}")
    print(f"  Won: {metrics['won']} | Lost: {metrics['lost']}")
    print(f"  Conversion Rate: {metrics['conversion_rate']:.1%}")
    if metrics.get('revenue'):
        print(f"  Total Revenue: ${metrics['revenue']['total']:,.0f}")
        print(f"  Avg Deal Size: ${metrics['revenue']['avg_deal_size']:,.0f}")

    return recorder


def demo_graveyard_learning(recorder):
    """Demo: Graveyard nutrients and pattern analysis"""
    print_section("5. GRAVEYARD SYSTEM - Learning from Failures")

    graveyard = GraveyardManager()

    # Get nutrients from outcomes
    nutrients_data = recorder.get_graveyard_nutrients()

    print(f"\n⚰️  Burying {len(nutrients_data)} failed leads...")
    for nutrient_data in nutrients_data:
        # Reconstruct outcome dict for graveyard
        outcome = {
            'lead_id': nutrient_data['lead_id'],
            'company_name': nutrient_data['company_name'],
            'outcome_type': nutrient_data['outcome_type'],
            'qualification_tier': nutrient_data['qualification_tier'],
            'coherence_score': nutrient_data['coherence_score'],
            'trial_branch': nutrient_data['trial_branch'],
            'learnings': {
                'what_went_wrong': nutrient_data['what_went_wrong'],
                'lesson_learned': nutrient_data['lesson_learned'],
            },
            'competitor_chosen': nutrient_data.get('competitor_chosen'),
            'loss_reason': nutrient_data.get('loss_reason'),
        }
        nutrients = graveyard.bury_lead(outcome)
        print(f"  {outcome['company_name']}: {len(nutrients)} nutrients extracted")

    # Analyze patterns
    print("\n🔍 Pattern Analysis:")
    patterns = graveyard.analyze_patterns()
    if patterns:
        for pattern in patterns[:3]:
            print(f"\n  {pattern.priority.upper()}: {pattern.pattern_type}")
            print(f"    Frequency: {pattern.frequency}")
            print(f"    Action: {pattern.recommended_action}")
    else:
        print("  Not enough data for pattern detection yet")

    # Critical nutrients
    print("\n⚠️  Critical Nutrients (Need Immediate Attention):")
    critical = graveyard.get_critical_nutrients()
    if critical:
        for nutrient in critical[:3]:
            print(f"\n  {nutrient.category.upper()}: {nutrient.lesson}")
            print(f"    From: {nutrient.company_name} (C={nutrient.coherence_score:.2f})")
    else:
        print("  None yet - need more high-value losses")

    return graveyard


def demo_trial_system():
    """Demo: A/B testing and evolution"""
    print_section("6. TRIAL SYSTEM - Evolutionary Learning")

    manager = TrialManager()

    print("\n🧪 Creating Experimental Trial:")
    trial = manager.create_trial(
        name="Authority-Weighted Lens",
        description="Test increasing ρ (authority) weight from 0.30 to 0.40",
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
        min_sample_size=10,  # Lower for demo
    )

    trial.start()
    print(f"  Trial ID: {trial.trial_id}")
    print(f"  Traffic Split: 50% classic / 50% experimental")

    # Simulate some qualifications (demo data)
    print("\n📊 Simulating lead qualifications...")
    import random
    for i in range(25):
        branch = trial.assign_branch()
        tier = random.choices(
            ['hot', 'warm', 'cold', 'disqualified'],
            weights=[0.15, 0.35, 0.30, 0.20]
        )[0]
        manager.record_qualification(trial.trial_id, branch, tier)

        # Simulate some outcomes
        if random.random() < 0.4:  # 40% get outcomes
            outcome = random.choices(['won', 'lost'], weights=[0.35, 0.65])[0]
            deal_value = random.randint(20000, 80000) if outcome == 'won' else 0
            manager.record_outcome(trial.trial_id, branch, outcome, deal_value, cost=5000)

    print(f"  Classic: {trial.classic_branch.leads_qualified} qualified")
    print(f"  Experimental: {trial.experimental_branch.leads_qualified} qualified")

    # Evaluate
    print("\n📈 Evaluating Trial:")
    if trial.is_ready_for_evaluation():
        result = manager.evaluate_trial(trial.trial_id)

        print(f"\n  🏆 Winner: {result.winner.upper()}")
        print(f"  Confidence: {result.confidence:.1%}")
        print(f"  Improvement: {result.improvement:.1f}%")
        print(f"  Recommendation: {result.recommendation.upper()}")
        print(f"  Rationale: {result.rationale}")

        if result.recommendation == 'promote':
            print("\n  🚀 Experimental approach would be promoted to standard!")
        elif result.recommendation == 'archive':
            print("\n  📦 Experimental approach would be archived (classic won)")
        else:
            print("\n  ⏳ Need more data - trial would continue")
    else:
        print("  Not enough data yet for evaluation")

    return trial


def main():
    """Run complete system demo"""
    print("\n" + "=" * 70)
    print("  ROSE GLASS CERATA CRM - SYSTEM DEMONSTRATION")
    print("  Perceive, Evolve, Learn")
    print("=" * 70)

    try:
        # Run all demos
        leads1 = demo_rose_glass_perception()
        leads2 = demo_hunter_engines()
        all_leads = leads1 + leads2

        results = demo_qualification_pipeline(all_leads)
        recorder = demo_outcome_recording(results)
        graveyard = demo_graveyard_learning(recorder)
        trial = demo_trial_system()

        # Summary
        print_section("✅ DEMO COMPLETE - All Systems Operational")
        print("\nComponents Validated:")
        print("  ✓ Rose Glass Lens - Dimensional perception")
        print("  ✓ Hunter Engines - Lead discovery & ingestion")
        print("  ✓ Qualification Pipeline - Tier assignment & routing")
        print("  ✓ Outcome Recording - Metrics & learnings")
        print("  ✓ Graveyard System - Nutrient extraction & patterns")
        print("  ✓ Trial System - A/B testing & evolution")

        print("\nNext Steps:")
        print("  1. Review CERATA_CRM.md for philosophy")
        print("  2. Customize lens in config/lenses/")
        print("  3. Run with your own lead data")
        print("  4. Monitor trial evolution")
        print("  5. Learn from graveyard nutrients")

        print("\n" + "=" * 70)
        print("  🌹 Rose Glass sees all, judges none, learns always")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
