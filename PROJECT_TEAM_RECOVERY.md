# Rose Glass Cerata CRM - Team Recovery Draper, Utah

## Project Overview

**Client**: Team Recovery
**Location**: Draper, Utah
**Industry**: Behavioral Health / Addiction Recovery Services
**Purpose**: Intelligent lead qualification and crisis detection for admissions

## Mission Statement

Use Rose Glass perception to:
1. **Detect crisis urgency** in incoming leads (safety-first approach)
2. **Qualify readiness** for recovery treatment
3. **Match services** to individual needs
4. **Learn from outcomes** to improve admission success rates
5. **Evolve approaches** through trial-based optimization

## System Adaptation for Recovery Services

### Rose Glass Dimensions - Recovery Context

**Ψ (psi) - Intent Coherence**: Readiness for change
- Self-referred vs. court-ordered vs. family intervention
- Expressed desire for help
- Previous treatment attempts
- Recognition of problem

**ρ (rho) - Authority/Resources**: Ability to access treatment
- Insurance coverage (Medicaid, private, self-pay)
- Family support system
- Decision-making capacity (legal guardian, self)
- Financial resources verified

**q - Urgency/Activation**: Safety and timeline
- **CRITICAL**: Immediate safety risk (suicidal ideation, overdose risk)
- Withdrawal symptoms requiring medical supervision
- Legal timeline (court-ordered deadline)
- Environmental danger (unstable living situation)

**f - Fit/Belonging**: Treatment program match
- Substance of choice matches program specialty
- Age/gender fit for group cohorts
- Co-occurring disorders (dual diagnosis capabilities)
- Geographic accessibility (local vs. out-of-state)

### Qualification Tiers - Recovery Context

| Tier | Description | Coherence | Next Action | Timeline |
|------|-------------|-----------|-------------|----------|
| **CRISIS** | Immediate safety risk | Any C with q > 0.7 | Medical assessment NOW | < 2 hours |
| **HOT** | Ready, able, urgent | C ≥ 2.5 | Admission within 24-48h | < 2 days |
| **WARM** | Interested, needs verification | C ≥ 1.5 | Insurance verification, assessment scheduled | 3-7 days |
| **COLD** | Early inquiry, not ready | C ≥ 0.5 | Educational nurture, family support | 30+ days |
| **NOT READY** | Not appropriate for treatment now | C < 0.5 | Referral to other resources | Archive |

## Implementation Plan

### Phase 1: Setup & Configuration (Week 1)

#### 1.1 Environment Setup

```bash
# On Team Recovery admissions workstation
cd ~/Documents
git clone https://github.com/GreatPyreneseDad/RoseGlassCerataCRM.git
cd RoseGlassCerataCRM

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 demo.py
```

#### 1.2 Create Recovery-Specific Lens

Create `config/lenses/team_recovery.yaml`:

```yaml
name: team_recovery_draper
description: Recovery services lens for Team Recovery, Draper UT

weights:
  psi_intent: 0.25      # Readiness for change
  rho_authority: 0.30   # Resources/insurance
  q_urgency: 0.30       # Safety/timeline (higher for crisis detection)
  f_fit: 0.15           # Program match

# Crisis detection threshold (overrides normal tiers)
crisis_threshold: 0.7   # q_urgency above this = CRISIS tier

# Authority threshold (insurance/resources)
authority_threshold: 0.4  # Lower than enterprise (recovery accepts Medicaid)

# Hot tier requirements
hot_tier:
  min_coherence: 2.5
  min_authority: 0.4    # Has verified coverage
  min_urgency: 0.3

# Intent signals - Recovery context
intent_signals:
  sources:
    self_referral: 0.35      # Strong indicator
    family_referral: 0.30
    therapist_referral: 0.35
    court_ordered: 0.20      # Lower intent (external pressure)
    er_referral: 0.40        # High crisis
    unknown: 0.05

  engagement:
    called_directly: 0.20
    filled_inquiry_form: 0.15
    previous_treatment: 0.10   # Shows pattern of seeking help
    family_involved: 0.15

# Authority signals - Resources/Insurance
authority_signals:
  insurance_verified: 0.40
  insurance_pending: 0.20
  self_pay_committed: 0.35
  family_support: 0.15

  coverage_types:
    private_insurance: 0.25
    medicaid: 0.20
    medicare: 0.20
    self_pay: 0.15
    uninsured: 0.05

# Urgency signals - Safety & Timeline
urgency_signals:
  crisis_keywords:
    - suicidal
    - overdose
    - withdrawal
    - detox needed
    - immediate danger
    - unsafe
    - homeless
    - court deadline
    - probation
    - CPS involved

  timeline:
    immediate: 0.50      # "I need help now"
    this_week: 0.40
    this_month: 0.25
    exploring: 0.10

# Fit signals - Program match
fit_signals:
  substances_match:
    - alcohol
    - opioids
    - stimulants
    - benzodiazepines
    - cannabis
    - polysubstance

  demographics:
    adults_18_plus: 0.20
    gender_appropriate: 0.15
    dual_diagnosis_capable: 0.20

  location:
    utah_resident: 0.15
    out_of_state_acceptable: 0.10

# Warning signals
warning_signals:
  not_ready:
    - "just looking"
    - "not sure I have a problem"
    - "family made me call"
    - "court making me"

  clinical_concerns:
    - severe mental health crisis (needs psychiatric hospital)
    - active psychosis
    - violent behavior
    - medical emergency (call 911)

# Crisis escalation
crisis_escalation:
  suicide_keywords:
    - suicidal
    - want to die
    - end my life
    - kill myself

  medical_emergency:
    - overdosed
    - chest pain
    - can't breathe
    - unresponsive

  action: "IMMEDIATE clinical assessment required - contact crisis clinician"
```

#### 1.3 Create Hunt Criteria Template

Create `config/hunting/team_recovery_hunt.py`:

```python
from src.hunter.web_hunter import HuntCriteria

# Team Recovery hunt criteria
TEAM_RECOVERY_HUNT = HuntCriteria(
    target_industries=[
        'healthcare',
        'mental health',
        'employee assistance programs',
        'legal services',
        'probation offices',
    ],

    pain_keywords=[
        'addiction treatment',
        'substance abuse help',
        'alcohol rehab',
        'opioid treatment',
        'drug recovery',
        'family intervention',
        'court ordered treatment',
    ],

    solution_keywords=[
        'residential treatment',
        'outpatient program',
        'detox services',
        'dual diagnosis',
        'recovery support',
    ],

    regions=[
        'Utah',
        'Salt Lake City',
        'Draper',
        'Provo',
        'Ogden',
    ],

    # Don't hunt competitors
    exclude_competitors=[
        'Cirque Lodge',
        'Renaissance Ranch',
        'Odyssey House',
    ],

    max_results_per_hunt=25,
)
```

### Phase 2: Data Integration (Week 2)

#### 2.1 Import Existing Leads

Team Recovery likely has leads from:
- Phone inquiries (logged in spreadsheet or CRM)
- Web form submissions
- Referral sources (therapists, hospitals, courts)

**Import Process:**

```python
# import_team_recovery_leads.py
from pathlib import Path
from src.hunter.data_hunter import DataHunter, FieldMapping
from src.pipeline.qualifier import LeadQualifier

# Create hunter
hunter = DataHunter()

# Define field mapping for Team Recovery's data format
# (Adjust based on actual column names)
team_recovery_mapping = FieldMapping(
    company_name='insurance_provider',  # Or use 'last_name' for individuals
    contact_name='full_name',
    contact_email='email',
    contact_title='relationship',  # self, parent, spouse, etc.

    # Custom fields
    pain_points='substance_of_concern',
    notes='inquiry_notes',
    source='referral_source',

    # Insurance/resources
    is_decision_maker='is_self',
    budget_mentioned='insurance_coverage',

    # Urgency
    timeline_mentioned='requested_start_date',
)

# Import from CSV export
leads = hunter.ingest_csv(
    Path('data/team_recovery_leads_2026.csv'),
    field_mapping=team_recovery_mapping
)

print(f"Imported {len(leads)} leads")

# Qualify through Team Recovery lens
qualifier = LeadQualifier(lens_name='team_recovery_draper', trial_branch='classic')
results = qualifier.qualify_batch(leads)

# Review crisis cases
crisis_leads = [r for r in results if r.coherence.q_urgency > 0.7]
print(f"\n🚨 CRISIS CASES: {len(crisis_leads)}")
for lead in crisis_leads:
    print(f"  {lead.company_name} - q={lead.coherence.q_urgency:.2f}")
    print(f"    Actions: {', '.join(lead.coherence.next_actions)}")

# Review hot leads (ready for admission)
hot_leads = [r for r in results if r.qualification_tier == 'hot']
print(f"\n🔥 HOT LEADS (Ready for admission): {len(hot_leads)}")
for lead in hot_leads:
    print(f"  {lead.company_name} - C={lead.coherence.coherence_score:.2f}")

# Export for admissions team
qualifier.export_log(Path('data/leads/qualified_leads.json'))
```

#### 2.2 Daily Inquiry Processing

Create `process_daily_inquiries.py`:

```python
#!/usr/bin/env python3
"""
Daily inquiry processing for Team Recovery
Runs each morning to qualify new leads from previous day
"""

from pathlib import Path
from datetime import datetime, timedelta
from src.hunter.data_hunter import DataHunter
from src.pipeline.qualifier import LeadQualifier
import json

def process_daily_inquiries():
    """Process yesterday's inquiries"""

    # Load new inquiries (from CRM export or web form database)
    hunter = DataHunter()

    # Example: Load from daily export
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    export_file = Path(f"exports/inquiries_{yesterday.strftime('%Y%m%d')}.csv")

    if not export_file.exists():
        print(f"No inquiries for {yesterday.strftime('%Y-%m-%d')}")
        return

    leads = hunter.ingest_csv(export_file)
    print(f"\n📥 Processing {len(leads)} inquiries from {yesterday.strftime('%Y-%m-%d')}")

    # Qualify
    qualifier = LeadQualifier(lens_name='team_recovery_draper')
    results = qualifier.qualify_batch(leads)

    # Generate priority lists
    crisis = [r for r in results if r.coherence.q_urgency > 0.7]
    hot = [r for r in results if r.qualification_tier == 'hot']
    warm = [r for r in results if r.qualification_tier == 'warm']

    # Create daily briefing
    briefing = {
        'date': today.isoformat(),
        'total_inquiries': len(leads),
        'crisis_count': len(crisis),
        'hot_count': len(hot),
        'warm_count': len(warm),
        'crisis_leads': [
            {
                'name': r.company_name,
                'urgency': r.coherence.q_urgency,
                'actions': r.coherence.next_actions,
                'signals': r.coherence.warning_signals,
            }
            for r in crisis
        ],
        'hot_leads': [
            {
                'name': r.company_name,
                'coherence': r.coherence.coherence_score,
                'insurance_status': 'pending_verification',  # Update with actual data
                'actions': r.coherence.next_actions,
            }
            for r in hot
        ],
    }

    # Save briefing
    briefing_file = Path(f"reports/daily_briefing_{today.strftime('%Y%m%d')}.json")
    briefing_file.parent.mkdir(exist_ok=True)
    with open(briefing_file, 'w') as f:
        json.dump(briefing, f, indent=2)

    # Print summary for admissions team
    print("\n" + "="*60)
    print(f"  DAILY ADMISSIONS BRIEFING - {today.strftime('%B %d, %Y')}")
    print("="*60)

    if crisis:
        print(f"\n🚨 CRISIS CASES ({len(crisis)}) - IMMEDIATE ACTION REQUIRED")
        for r in crisis:
            print(f"\n  {r.company_name}")
            print(f"    Urgency: {r.coherence.q_urgency:.2f}")
            print(f"    Next: {r.coherence.next_actions[0]}")

    if hot:
        print(f"\n🔥 HOT LEADS ({len(hot)}) - Ready for Admission")
        for r in hot[:5]:  # Top 5
            print(f"  • {r.company_name} (C={r.coherence.coherence_score:.2f})")

    if warm:
        print(f"\n📋 WARM LEADS ({len(warm)}) - Needs Follow-up")

    print(f"\n✓ Briefing saved to: {briefing_file}")
    print("="*60)

if __name__ == "__main__":
    process_daily_inquiries()
```

### Phase 3: Workflow Integration (Week 3)

#### 3.1 Admissions Team Workflow

**Morning Routine (8:00 AM):**

```bash
# Run daily processing
python3 process_daily_inquiries.py

# Review briefing
cat reports/daily_briefing_$(date +%Y%m%d).json | jq
```

**Crisis Protocol:**
1. Rose Glass detects `q > 0.7` → CRISIS tier
2. System flags lead with crisis keywords
3. Admissions coordinator **immediately** contacts crisis clinician
4. Clinical assessment within 2 hours
5. Medical clearance if needed
6. Bed assignment same day if appropriate

**Hot Lead Protocol:**
1. Rose Glass assigns HOT tier (C ≥ 2.5)
2. Insurance verification within 4 hours
3. Clinical assessment scheduled within 24 hours
4. Admission coordinator follows up daily
5. Goal: Admission within 48 hours

**Warm Lead Protocol:**
1. Rose Glass assigns WARM tier
2. Initial insurance inquiry sent
3. Educational materials provided
4. Follow-up call in 3 days
5. Re-qualify after insurance verification

#### 3.2 Manual Lead Entry (Phone Inquiries)

Create `add_phone_inquiry.py`:

```python
#!/usr/bin/env python3
"""Quick lead entry for phone inquiries"""

from src.hunter.data_hunter import DataHunter
from src.pipeline.qualifier import LeadQualifier

def add_phone_inquiry():
    """Interactive lead entry"""

    print("\n" + "="*60)
    print("  TEAM RECOVERY - PHONE INQUIRY ENTRY")
    print("="*60)

    # Collect information
    name = input("\nFull Name: ")
    phone = input("Phone: ")
    email = input("Email (optional): ") or None

    print("\nReferral Source:")
    print("  1. Self")
    print("  2. Family")
    print("  3. Therapist/Provider")
    print("  4. Court/Legal")
    print("  5. ER/Hospital")
    source_map = {
        '1': 'self_referral',
        '2': 'family_referral',
        '3': 'therapist_referral',
        '4': 'court_ordered',
        '5': 'er_referral',
    }
    source = source_map.get(input("Select (1-5): "), 'unknown')

    substance = input("\nSubstance of concern: ")
    insurance = input("Insurance provider (or 'self-pay'): ")

    print("\nUrgency:")
    print("  1. Immediate (crisis/safety concern)")
    print("  2. This week")
    print("  3. This month")
    print("  4. Exploring options")
    timeline_map = {
        '1': 'immediate',
        '2': 'this_week',
        '3': 'this_month',
        '4': 'exploring',
    }
    timeline = timeline_map.get(input("Select (1-4): "), 'exploring')

    notes = input("\nAdditional notes: ")

    # Create lead
    hunter = DataHunter()
    lead = hunter.create_manual_lead(
        company_name=name,  # For individuals, use name
        contact_name=name,
        contact_email=email,
        industry='recovery_services',
        pain_points=[substance] if substance else [],
        source=source,
        timeline_mentioned=timeline,
        notes=f"Phone inquiry. Insurance: {insurance}. {notes}",
    )

    # Qualify immediately
    qualifier = LeadQualifier(lens_name='team_recovery_draper')
    result = qualifier.qualify(lead)

    # Display result
    print("\n" + "="*60)
    print("  QUALIFICATION RESULT")
    print("="*60)
    print(f"\nTier: {result.qualification_tier.upper()}")
    print(f"Coherence: {result.coherence.coherence_score:.2f} / 4.0")
    print(f"Priority: {result.priority_score:.2f}")

    if result.coherence.q_urgency > 0.7:
        print("\n🚨 CRISIS ALERT - Immediate clinical assessment required!")

    print(f"\nNext Actions:")
    for action in result.coherence.next_actions:
        print(f"  • {action}")

    if result.coherence.warning_signals:
        print(f"\n⚠️  Warnings:")
        for warning in result.coherence.warning_signals:
            print(f"  • {warning}")

    print("\n" + "="*60)

    # Save
    save = input("\nSave lead? (y/n): ")
    if save.lower() == 'y':
        # Save to pending admissions file
        import json
        from pathlib import Path
        from datetime import datetime

        pending_file = Path('data/leads/pending_admissions.json')

        # Load existing
        if pending_file.exists():
            with open(pending_file) as f:
                pending = json.load(f)
        else:
            pending = []

        # Add new lead
        pending.append({
            'lead_id': lead.lead_id,
            'name': name,
            'phone': phone,
            'email': email,
            'source': source,
            'substance': substance,
            'insurance': insurance,
            'timeline': timeline,
            'notes': notes,
            'qualification': result.to_dict(),
            'entered_at': datetime.now().isoformat(),
        })

        # Save
        pending_file.parent.mkdir(parents=True, exist_ok=True)
        with open(pending_file, 'w') as f:
            json.dump(pending, f, indent=2)

        print(f"\n✓ Lead saved: {lead.lead_id}")
        print(f"  Next: {result.next_stage}")

if __name__ == "__main__":
    add_phone_inquiry()
```

### Phase 4: Outcome Tracking & Learning (Week 4)

#### 4.1 Track Admissions & Outcomes

Create `record_outcome.py`:

```python
#!/usr/bin/env python3
"""Record admission outcomes for learning"""

from src.pipeline.outcome import OutcomeRecorder, OutcomeType
from datetime import datetime, timedelta

recorder = OutcomeRecorder()

# Example: Successful admission
recorder.record_won(
    lead_id='lead_001',
    company_name='John Doe',
    deal_value=25000,  # 30-day program cost
    qualification_tier='hot',
    coherence_score=3.1,
    trial_branch='classic',
    first_contact_at=datetime.now() - timedelta(days=2),
    what_went_right=[
        'Family support secured',
        'Insurance verified quickly',
        'High readiness for change',
    ],
)

# Example: Lost to competing facility
recorder.record_lost(
    lead_id='lead_002',
    company_name='Jane Smith',
    loss_type=OutcomeType.LOST_TO_COMPETITOR,
    expected_value=25000,
    qualification_tier='warm',
    coherence_score=2.3,
    competitor_chosen='Cirque Lodge',
    loss_reason='Wanted luxury accommodations',
    what_went_wrong=['Price objection', 'Preferred mountain location'],
    lesson_learned='Luxury segment needs different positioning',
)

# Example: Lead not ready
recorder.record_lost(
    lead_id='lead_003',
    company_name='Bob Wilson',
    loss_type=OutcomeType.LOST_NO_DECISION,
    qualification_tier='warm',
    coherence_score=1.8,
    loss_reason='Family intervention failed - individual not ready',
    what_went_wrong=['Low internal motivation', 'Family pressure only'],
    lesson_learned='Need stronger readiness assessment for family referrals',
)

# Get metrics
metrics = recorder.get_conversion_metrics()
print("\n📊 Admissions Metrics:")
print(f"  Conversion Rate: {metrics['conversion_rate']:.1%}")
print(f"  Average Program Value: ${metrics['revenue']['avg_deal_size']:,.0f}")
```

#### 4.2 Monthly Graveyard Review

Create `monthly_graveyard_review.py`:

```python
#!/usr/bin/env python3
"""Monthly review of failed admissions for learning"""

from src.graveyard.graveyard_manager import GraveyardManager
from src.pipeline.outcome import OutcomeRecorder

# Get failed admissions
recorder = OutcomeRecorder()
nutrients_data = recorder.get_graveyard_nutrients()

# Bury in graveyard
graveyard = GraveyardManager()
print(f"\n⚰️  Burying {len(nutrients_data)} failed admissions...")

for nutrient_data in nutrients_data:
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
    graveyard.bury_lead(outcome)

# Analyze patterns
print("\n🔍 Pattern Analysis:")
patterns = graveyard.analyze_patterns()

for pattern in patterns:
    print(f"\n{pattern.priority.upper()}: {pattern.pattern_type}")
    print(f"  Frequency: {pattern.frequency}")
    print(f"  Recommendation: {pattern.recommended_action}")

# Critical nutrients
print("\n⚠️  Critical Learnings:")
critical = graveyard.get_critical_nutrients()
for nutrient in critical:
    print(f"\n{nutrient.category.upper()}: {nutrient.lesson}")
    print(f"  From: {nutrient.company_name}")

# Export for review
from pathlib import Path
graveyard.export_insights(Path('reports/monthly_graveyard_insights.json'))
print("\n✓ Insights exported for team review")
```

### Phase 5: Evolution Through Trials (Ongoing)

#### 5.1 Create Experimental Approach

Based on graveyard learnings, test new qualification approaches:

```python
# test_new_lens.py
from src.trial.trial_manager import TrialManager

manager = TrialManager()

# Example: Test if increasing urgency weight improves crisis detection
trial = manager.create_trial(
    name="Increased Crisis Detection",
    description="Test q_urgency weight of 0.40 (from 0.30) for better crisis identification",
    experimental_config={
        'lens': 'team_recovery_draper',
        'weights': {
            'psi_intent': 0.20,
            'rho_authority': 0.25,
            'q_urgency': 0.40,  # Increased from 0.30
            'f_fit': 0.15,
        },
        'crisis_threshold': 0.65,  # Lowered from 0.70 for earlier detection
    },
    traffic_split=0.5,  # 50/50 split
    min_sample_size=50,
)

trial.start()
print(f"✓ Trial started: {trial.trial_id}")
print("  Next 50 leads will be split 50/50 between classic and experimental")
```

#### 5.2 Monitor Trial Progress

```python
# check_trial.py
from src.trial.trial_manager import TrialManager

manager = TrialManager()
trial = manager.get_active_trial()

if trial:
    print(f"\n📊 Active Trial: {trial.name}")
    print(f"  Classic: {trial.classic_branch.leads_qualified} leads")
    print(f"  Experimental: {trial.experimental_branch.leads_qualified} leads")

    if trial.is_ready_for_evaluation():
        print("\n✓ Ready for evaluation!")
        result = manager.evaluate_trial(trial.trial_id)

        if result.recommendation == 'promote':
            print(f"\n🚀 Experimental approach won!")
            print(f"  Improvement: {result.improvement:.1f}%")
            manager.promote_experimental(trial.trial_id)
else:
    print("No active trial")
```

## Privacy & Compliance Considerations

### HIPAA Compliance

**Data Storage:**
- All lead data contains PHI (Protected Health Information)
- Store `data/` directory on encrypted drive
- Limit access to admissions team only
- Never commit actual lead data to Git (use .gitignore)

**Security Measures:**

```bash
# Encrypt data directory
# macOS:
diskutil apfs addVolume disk1 APFS "TeamRecovery-Encrypted" -encryption

# Store data on encrypted volume
mkdir /Volumes/TeamRecovery-Encrypted/RoseGlass-Data
ln -s /Volumes/TeamRecovery-Encrypted/RoseGlass-Data ./data
```

**Access Control:**
- Admissions staff only
- Audit log of all queries
- No email of lead data (use secure portal)

### Crisis Protocol - Legal Disclaimer

**IMPORTANT**: Rose Glass CRM is a **qualification tool**, not a clinical assessment.

- `q > 0.7` = FLAG for clinical review
- System cannot diagnose
- Licensed clinician MUST assess all crisis flags
- Document all crisis interventions
- Have backup crisis line: National Suicide Prevention: 988

## Training Materials

### For Admissions Team

**30-Minute Onboarding:**

1. **Concept** (5 min): Rose Glass sees readiness, resources, urgency, fit
2. **Demo** (10 min): Run `python3 add_phone_inquiry.py` with sample cases
3. **Daily Workflow** (10 min): Morning briefing, crisis protocol, follow-up
4. **Practice** (5 min): Enter 3 sample leads

**Cheat Sheet:**

```
CRISIS (q > 0.7): Contact crisis clinician IMMEDIATELY
HOT (C ≥ 2.5): Admission within 48h - verify insurance, schedule assessment
WARM (C ≥ 1.5): Follow-up in 3 days - insurance inquiry, education
COLD (C < 1.5): Long-term nurture - monthly check-in
NOT READY: Referral to other resources, archive
```

### For Clinical Team

**Understanding Rose Glass Tiers:**

- **Not a diagnosis** - it's a qualification signal
- **Urgency detection** helps prioritize assessments
- **Clinical judgment** always overrides system
- **Learn from outcomes** - your feedback improves the system

## Success Metrics

### Month 1 Goals

- [ ] 100+ leads qualified through Rose Glass
- [ ] Crisis detection: 100% of flagged cases reviewed within 2 hours
- [ ] Hot lead conversion: Track baseline (target 40%+)
- [ ] Team comfort with system: 4/5 satisfaction

### Month 3 Goals

- [ ] First trial evaluated (experimental approach tested)
- [ ] Graveyard insights: 3+ actionable patterns identified
- [ ] Improved crisis detection accuracy (measured by clinician feedback)
- [ ] Reduced time-to-admission for hot leads (target < 48h)

### Month 6 Goals

- [ ] 2+ successful experimental promotions
- [ ] Conversion rate improvement: +15% from baseline
- [ ] Automated daily processing
- [ ] Integrated with CRM (if applicable)

## Support & Maintenance

### Weekly Tasks

- Monday AM: Run `python3 process_daily_inquiries.py` for weekend leads
- Daily AM: Review briefing, follow crisis protocol
- Friday PM: Export weekly stats for team meeting

### Monthly Tasks

- Run `python3 monthly_graveyard_review.py`
- Review trial progress
- Update lens calibration based on learnings
- Team retrospective: What's working? What needs adjustment?

### Quarterly Tasks

- Evaluate all active trials
- Promote winning approaches
- Create new experiments from graveyard insights
- System audit: Privacy compliance, data cleanup

## Troubleshooting

### Common Issues

**Issue**: "Crisis leads not being flagged"
- **Check**: `q_urgency` calculation in `team_recovery.yaml`
- **Fix**: Lower `crisis_threshold` from 0.7 to 0.6
- **Test**: Run demo with known crisis keywords

**Issue**: "Too many false positives (not actually ready)"
- **Check**: `psi_intent` might be too generous
- **Fix**: Increase weight on `rho_authority` (resources verification)
- **Test**: Create trial with adjusted weights

**Issue**: "System says 'HOT' but they don't have insurance"
- **Check**: Insurance verification in qualification
- **Fix**: Update `authority_signals` to require verified coverage
- **Test**: Add leads with/without insurance

## Contact & Support

**Project Lead**: [Your Name]
**Email**: [your-email]
**Emergency**: If system is down during crisis, fallback to manual triage

**GitHub Issues**: https://github.com/GreatPyreneseDad/RoseGlassCerataCRM/issues

---

## Quick Start Checklist

- [ ] Clone repository
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Create `team_recovery.yaml` lens
- [ ] Run demo to verify installation
- [ ] Import existing leads (if any)
- [ ] Train admissions team (30 min)
- [ ] Set up daily processing script
- [ ] Document crisis protocol
- [ ] Begin tracking outcomes
- [ ] Schedule month 1 review

---

**Remember**: Rose Glass **perceives patterns**, clinicians make **medical decisions**. This system enhances, not replaces, clinical judgment.

🌹 *Rose Glass sees all, judges none, learns always*
