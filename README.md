# Rose Glass Cerata CRM

**Evolving Lead Generation Agent** using Rose Glass dimensional perception and CERATA biological metabolism.

## What is This?

A CRM system that **perceives** lead quality through 4-dimensional coherence analysis and **evolves** through A/B trials—inspired by biological systems, not traditional scoring.

### Key Concepts

- **Rose Glass**: Perception lens translating raw lead data into coherent dimensions (Ψ, ρ, q, f)
- **CERATA**: Biological metabolism framework where failures become nutrients for evolution
- **No Manual Tuning**: System evolves through trials, promoting winning approaches
- **Graveyard Learning**: Failed leads decompose into insights that inform experiments

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/rose-glass-cerata-crm.git
cd rose-glass-cerata-crm

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in dev mode
pip install -e .
```

### Basic Usage

```python
from src.core.rose_glass_lens import RoseGlassCRMLens, LeadData
from src.pipeline.qualifier import LeadQualifier

# Create a lead
lead = LeadData(
    lead_id='demo001',
    company_name='Acme Corp',
    contact_name='John Smith',
    contact_title='VP Engineering',
    industry='SaaS',
    company_size='enterprise',
    pain_points=['security compliance', 'access management'],
    source='referral',
    is_decision_maker=True,
    budget_mentioned=True,
    timeline_mentioned='this_quarter',
)

# Qualify through Rose Glass
qualifier = LeadQualifier(lens_name='enterprise_saas')
result = qualifier.qualify(lead)

print(f"Qualification: {result.qualification_tier.upper()}")
print(f"Coherence: {result.coherence.coherence_score:.2f}")
print(f"Next Actions: {', '.join(result.coherence.next_actions)}")
```

**Output:**
```
🔍 Qualifying: Acme Corp (ID: demo001)
  → HOT: C=3.25 (Ψ=0.75, ρ=0.80, q=0.65, f=0.70) → active_sales
  ✓ Signals: Decision-making authority, Strong intent signals, Urgency expressed

Qualification: HOT
Coherence: 3.25
Next Actions: Schedule demo/meeting ASAP, Confirm budget in first call
```

## Architecture

```
RoseGlassCerataCRM/
├── src/
│   ├── core/              # Rose Glass perception engine
│   │   ├── rose_glass_lens.py    # Core dimensional perception
│   │   └── __init__.py
│   ├── hunter/            # Lead discovery engines
│   │   ├── web_hunter.py         # Web search-based hunting
│   │   ├── data_hunter.py        # CSV/JSON/manual ingestion
│   │   └── __init__.py
│   ├── pipeline/          # Lead qualification pipeline
│   │   ├── qualifier.py          # Rose Glass qualification
│   │   ├── outcome.py            # Outcome recording & metrics
│   │   └── __init__.py
│   ├── graveyard/         # Learning from failures
│   │   ├── graveyard_manager.py  # Nutrient extraction & patterns
│   │   └── __init__.py
│   └── trial/             # A/B testing & evolution
│       ├── trial_manager.py      # Trial management & promotion
│       └── __init__.py
├── data/                  # Storage directories
│   ├── leads/
│   ├── graveyard/
│   ├── outcomes/
│   └── trials/
├── config/                # Configuration files
│   └── lenses/            # Industry lens calibrations
├── tests/                 # Test suite
├── CERATA_CRM.md         # Prime directive (philosophy)
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Components

### 1. Rose Glass Lens (Core Perception)

**Dimensions:**
- **Ψ (psi)**: Intent Coherence - Does their need match our solution?
- **ρ (rho)**: Decision Authority - Can they actually buy?
- **q**: Urgency/Activation - When do they need it?
- **f**: Fit/Belonging - Do they belong in our ecosystem?

**Coherence Formula:**
```
C = Ψ + (ρ × Ψ) + q_opt + (f × Ψ) + coupling

Where:
  q_opt = q / (Km + q + q²/Ki)  # Biological optimization
  coupling = 0.15 × ρ × Ψ       # Authority-intent reinforcement
```

**Tiers:**
- **HOT** (C ≥ 2.5): Immediate sales action
- **WARM** (C ≥ 1.5): Active nurture sequence
- **COLD** (C ≥ 0.5): Long-term nurture
- **DISQUALIFIED** (C < 0.5): Graveyard for learning

### 2. Hunter Engines

**WebHunter:**
```python
from src.hunter.web_hunter import WebHunter, HuntCriteria

criteria = HuntCriteria(
    target_industries=['SaaS', 'Fintech'],
    company_sizes=['mid-market', 'enterprise'],
    pain_keywords=['security compliance', 'access control'],
    exclude_competitors=['Competitor X'],
)

hunter = WebHunter()
results = await hunter.hunt(criteria)  # Returns HuntResult objects
```

**DataHunter:**
```python
from src.hunter.data_hunter import DataHunter

hunter = DataHunter()

# From CSV
leads = hunter.ingest_csv(Path('leads.csv'))

# From JSON
leads = hunter.ingest_json(Path('leads.json'))

# Manual entry
lead = hunter.create_manual_lead(
    company_name='Acme Corp',
    contact_name='John Smith',
    industry='SaaS',
)
```

### 3. Qualification Pipeline

```python
from src.pipeline.qualifier import LeadQualifier

qualifier = LeadQualifier(lens_name='enterprise_saas', trial_branch='classic')

# Qualify single lead
result = qualifier.qualify(lead)

# Batch qualification
results = qualifier.qualify_batch(leads)

# Export metrics for trial analysis
qualifier.export_log(Path('qualification_log.json'))
```

### 4. Outcome Recording

```python
from src.pipeline.outcome import OutcomeRecorder, OutcomeType

recorder = OutcomeRecorder()

# Record won deal
recorder.record_won(
    lead_id='hot001',
    company_name='Acme Corp',
    deal_value=50000,
    qualification_tier='hot',
    coherence_score=3.2,
)

# Record loss
recorder.record_lost(
    lead_id='warm002',
    company_name='Beta Corp',
    loss_type=OutcomeType.LOST_TO_COMPETITOR,
    competitor_chosen='Competitor X',
    what_went_wrong=['Lost on price', 'Did not multi-thread'],
    lesson_learned='Need better competitive positioning',
)

# Get metrics
metrics = recorder.get_conversion_metrics(trial_branch='classic')

# Extract nutrients for graveyard
nutrients = recorder.get_graveyard_nutrients()
```

### 5. Graveyard System

```python
from src.graveyard.graveyard_manager import GraveyardManager

graveyard = GraveyardManager()

# Bury failed lead
nutrients = graveyard.bury_lead(outcome_dict)

# Analyze patterns across failures
patterns = graveyard.analyze_patterns()

# Get critical learnings
critical = graveyard.get_critical_nutrients()

# Export insights for trials
graveyard.export_insights(Path('graveyard_insights.json'))
```

### 6. Trial System (Evolution)

```python
from src.trial.trial_manager import TrialManager

manager = TrialManager()

# Create experiment
trial = manager.create_trial(
    name="Authority-Weighted Lens",
    description="Test increasing ρ weight from 0.30 to 0.40",
    experimental_config={
        'lens': 'enterprise_saas',
        'weights': {
            'psi_intent': 0.20,
            'rho_authority': 0.40,  # Increased!
            'q_urgency': 0.20,
            'f_fit': 0.20,
        }
    },
    traffic_split=0.5,  # 50/50 split
    min_sample_size=50,
)

trial.start()

# ... leads get qualified with branch assignment ...

# Evaluate when ready
result = manager.evaluate_trial(trial.trial_id)

# If experimental wins
if result.recommendation == 'promote':
    manager.promote_experimental(trial.trial_id)  # Becomes new standard!
```

## Lens Calibrations

Pre-configured for different industries:

| Lens | Ψ (Intent) | ρ (Authority) | q (Urgency) | f (Fit) | Authority Threshold |
|------|------------|---------------|-------------|---------|---------------------|
| `enterprise_saas` | 0.20 | **0.35** | 0.20 | 0.25 | 0.60 |
| `smb_tech` | **0.30** | 0.20 | **0.30** | 0.20 | 0.40 |
| `federal_gov` | 0.25 | 0.25 | 0.15 | **0.35** | 0.50 |
| `healthcare` | 0.20 | 0.30 | 0.20 | **0.30** | 0.55 |

Create custom lenses in `config/lenses/`:

```yaml
# config/lenses/custom_lens.yaml
name: custom_fintech
weights:
  psi_intent: 0.25
  rho_authority: 0.35
  q_urgency: 0.20
  f_fit: 0.20
authority_threshold: 0.65
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_rose_glass_lens.py

# Run async tests
pytest tests/test_web_hunter.py -v
```

## Philosophy (CERATA Principles)

### 1. Perception, Not Scoring

**Traditional:**
```
Email open = +5 points
Website visit = +10 points
Total > 50? → Qualified
```

**Rose Glass:**
```
Extract Ψ, ρ, q, f dimensions
Calculate coherence with coupling
Biological optimization prevents gaming
Tier based on signal strength
```

### 2. Evolution, Not Configuration

**Traditional:**
```
Sales manager: "Let's change hot threshold to 55 points"
Developer: "Okay, done"
(No way to know if it helped)
```

**Rose Glass CERATA:**
```
Trial Manager: "Test threshold 2.4 vs 2.5"
System: Runs A/B trial with 100 leads
Winner: threshold 2.4 (10% more conversions)
System: Promotes to standard automatically
```

### 3. Learning, Not Deleting

**Traditional:**
```
Lost deal → Delete from pipeline
No record, no learning
```

**Rose Glass CERATA:**
```
Lost deal → Bury in graveyard
Extract nutrients (learnings)
Analyze patterns across failures
Feed insights to trial system
```

## Metrics

### Lead-Level
- **Coherence Score** (0-4): Overall signal strength
- **Qualification Tier**: hot/warm/cold/disqualified
- **Confidence** (0-1): Certainty of perception
- **Next Actions**: Recommended steps

### Trial Branch
- **Qualification Rate**: % not disqualified
- **Conversion Rate**: % won of qualified
- **Average Deal Value**: Revenue per win
- **Fitness Score**: Combined performance

### System Evolution
- **Standards Promoted**: Experiments that won
- **Active Nutrients**: Unresolved learnings
- **Pattern Frequency**: Recurring failure types

## Common Workflows

### Daily: Qualify New Leads

```python
# Ingest from CRM export
hunter = DataHunter()
leads = hunter.ingest_csv('daily_leads.csv')

# Qualify through active trial
qualifier = LeadQualifier(trial_branch=active_trial.assign_branch())
results = qualifier.qualify_batch(leads)

# Route by tier
hot_leads = [r for r in results if r.qualification_tier == 'hot']
warm_leads = [r for r in results if r.qualification_tier == 'warm']

# Take action
for lead in hot_leads:
    send_to_sales_team(lead, priority='immediate')
```

### Weekly: Review Graveyard

```python
graveyard = GraveyardManager()

# Analyze patterns
patterns = graveyard.analyze_patterns()

# Review critical nutrients
critical = graveyard.get_critical_nutrients()

# Create new experiment from pattern
if 'recurring_pricing_issues' in [p.pattern_type for p in patterns]:
    trial = manager.create_trial(
        name="Value-First Messaging",
        description="Test ROI calculator in initial outreach",
        experimental_config={'approach': 'value_first'},
    )
```

### Monthly: Evaluate Trials

```python
# Check active trial
trial = manager.get_active_trial()

if trial and trial.is_ready_for_evaluation():
    result = manager.evaluate_trial(trial.trial_id)

    if result.recommendation == 'promote':
        manager.promote_experimental(trial.trial_id)
        print(f"🚀 NEW STANDARD: {trial.experimental_branch.name}")

    elif result.recommendation == 'archive':
        manager.archive_trial(trial.trial_id)
        print(f"📦 Experiment failed, nutrients extracted")
```

## Roadmap

- [x] **v0.1**: Core Rose Glass perception
- [x] **v0.2**: Hunter engines (web + data)
- [x] **v0.3**: CERATA metabolism (graveyard + trials)
- [ ] **v0.4**: CRM integrations (Salesforce, HubSpot)
- [ ] **v0.5**: API endpoints & web dashboard
- [ ] **v0.6**: ML enhancements (deal value prediction)
- [ ] **v1.0**: Production deployment

## FAQ

**Q: Is this just lead scoring?**
A: No. Lead scoring is linear point addition. Rose Glass is dimensional perception with non-linear coupling. CERATA adds evolutionary learning.

**Q: Do I need to replace my CRM?**
A: No! This is a **perception layer** that enhances your CRM. It qualifies leads, recommends actions, and learns from outcomes.

**Q: How many leads before I see results?**
A: Immediate perception from day 1. Trial evaluation needs 50+ leads per branch. Full graveyard analysis requires 100+ outcomes.

**Q: What if I disagree with a qualification?**
A: Track overrides. If you consistently disagree, run a trial with different weights. Let data decide who's right.

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See [CERATA_CRM.md](CERATA_CRM.md) for philosophy
- **Issues**: [GitHub Issues](https://github.com/yourusername/rose-glass-cerata-crm/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rose-glass-cerata-crm/discussions)

---

**Rose Glass Cerata CRM** - *Perceive, Evolve, Learn*

*"In nature, the strongest survive not through brute force, but through adaptation."*
