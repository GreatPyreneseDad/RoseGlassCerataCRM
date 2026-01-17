# CERATA Trials - Evolution Through Competition

**Philosophy**: "Test everything, promote winners"

Trials pit experimental approaches against current standards. Winners become the new standard, losers feed the graveyard with learnings.

## Active Trials

### 1. Crawl4AI Enhanced Hunter

**Status**: Ready to run
**File**: `crawl4ai_hunter_trial.py`

**Comparison**:
- **Classic**: Requests-based synchronous scraping
- **Experimental**: Async Crawl4AI with LLM fallback

**Metrics**:
- Speed: Pages crawled per minute
- Accuracy: Lead extraction completeness
- Stealth: Success rate avoiding detection
- Richness: Average fields per lead

**Success Criteria**:
- 15%+ speed improvement
- 10%+ accuracy improvement
- Equal or better stealth

**How to Run**:

```bash
# Prerequisites
pip install crawl4ai playwright pydantic
playwright install

# Run trial demo
python trials/crawl4ai_hunter_trial.py

# Or integrate with your hunting code:
from trials.crawl4ai_hunter_trial import CrawlAIHunterTrial

trial = CrawlAIHunterTrial()
trial_id = trial.create_trial()
trial.trial.start()

# In your hunt loop:
branch = trial.trial.assign_branch()
if branch == 'experimental':
    # Use Crawl4AI
    results = await enhanced_hunter.hunt_leads(urls, schema)
else:
    # Use classic
    results = classic_hunter.scrape(urls)

# After min_sample_size (50+ URLs per branch):
recommendation = trial.evaluate()

if recommendation == 'promote':
    trial.promote()  # Experimental becomes standard!
```

**Expected Outcome**:
```
🧪 Created Crawl4AI Hunter Trial: trial_20260117_123456
  Classic: requests_based
  Experimental: async_crawl4ai
  Split: 50/50
  Min sample: 50 URLs per branch

🔍 Running hunt comparison on 3 URLs...

▶️  EXPERIMENTAL: Crawl4AI Enhanced Hunter
  ✓ Experimental complete:
    Duration: 5.23s
    Leads found: 47
    Success rate: 100.0%
    Avg coherence: 0.82
    Speed: 34.5 pages/min

▶️  CLASSIC: Traditional Web Hunter
  ✓ Classic complete:
    Duration: 26.15s (simulated)
    Leads found: 42 (simulated)
    Success rate: 80.0% (simulated)
    Speed: 6.9 pages/min

📊 TRIAL EVALUATION COMPLETE
  Winner: experimental
  Confidence: 95.2%
  Improvement: 42.3%
  Recommendation: PROMOTE
  Rationale: Experimental shows 42.3% improvement (fitness: 0.892 vs 0.627)

🚀 PROMOTED: Crawl4AI Enhanced Hunter → NEW STANDARD
  Classic hunter archived
  Enhanced hunter now default for web hunting
```

## Trial System Architecture

### Core Components

**TrialManager** (`src/trial/trial_manager.py`)
- Creates and manages trials
- Tracks metrics for classic vs experimental branches
- Evaluates results with statistical confidence
- Promotes winners, archives losers

**Trial**
- Represents one A/B test
- Contains two branches: classic and experimental
- Assigns traffic based on split ratio
- Tracks status: PLANNED → RUNNING → COMPLETED → PROMOTED/ARCHIVED

**TrialBranch**
- One side of the comparison
- Tracks metrics: leads_qualified, outcomes, revenue, cost
- Calculates fitness score for winner determination

**TrialResult**
- Evaluation outcome
- Winner, confidence, improvement %
- Recommendation: promote, continue, or archive

### Creating a New Trial

```python
from src.trial.trial_manager import TrialManager

manager = TrialManager()

trial = manager.create_trial(
    name="Your Trial Name",
    description="What you're testing",
    experimental_config={
        # Your experimental configuration
        'feature_x': True,
        'parameter_y': 0.8,
    },
    traffic_split=0.5,  # 50/50 split
    min_sample_size=50   # Min data points before evaluation
)

trial.start()
```

### Recording Metrics

```python
# Record a qualification
manager.record_qualification(
    trial_id=trial.trial_id,
    branch='experimental',  # or 'classic'
    tier='hot'  # or 'warm', 'cold', 'disqualified'
)

# Record an outcome
manager.record_outcome(
    trial_id=trial.trial_id,
    branch='experimental',
    outcome_type='won',  # or 'lost'
    deal_value=50000,
    cost=5000
)
```

### Evaluating and Promoting

```python
# Evaluate trial (requires min_sample_size per branch)
result = manager.evaluate_trial(trial.trial_id)

print(f"Winner: {result.winner}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Recommendation: {result.recommendation}")

# If experimental won:
if result.recommendation == 'promote':
    manager.promote_experimental(trial.trial_id)
    # Experimental becomes new standard!
```

## Metrics Mapping for Different Trial Types

### Lead Qualification Trials
- `leads_qualified`: Total leads processed
- `leads_hot/warm/cold`: Quality tiers
- `outcomes_won/lost`: Conversion results

### Web Hunting Trials (Crawl4AI)
- `leads_qualified`: URLs scraped
- `leads_hot`: High coherence extractions (≥0.8)
- `leads_warm`: Medium coherence (0.6-0.8)
- `leads_cold`: Low coherence (0.4-0.6)
- `leads_disqualified`: Failed scrapes (<0.4)
- `outcomes_won`: Successful crawls
- `outcomes_lost`: Failed/blocked crawls
- `deal_value`: Leads extracted × value per lead
- `total_cost`: LLM API costs

### ML Model Trials
- `leads_qualified`: Predictions made
- `leads_hot/warm/cold`: Confidence tiers
- `outcomes_won/lost`: Correct vs incorrect predictions
- `total_cost`: Inference costs

## Fitness Score Calculation

Each branch gets a fitness score:

```python
fitness = (
    qualification_rate * 0.3 +  # % not disqualified
    conversion_rate * 0.5 +      # % won of outcomes
    revenue_weight * 0.2         # Normalized avg deal value
)
```

Winner determined by:
- Experimental > Classic × 1.05 → Experimental wins
- Classic > Experimental × 1.05 → Classic wins
- Otherwise → Inconclusive, need more data

Confidence based on:
- Sample size (larger = higher confidence)
- Difference magnitude (bigger gap = higher confidence)

## Directory Structure

```
trials/
├── README.md                      # This file
├── crawl4ai_hunter_trial.py      # Crawl4AI vs classic hunter
├── ml_scorer_trial.py            # Future: ML lead scoring trial
└── ai_agent_trial.py             # Future: AI agent qualification trial

data/trials/
├── trial_YYYYMMDD_HHMMSS.json    # Trial state
├── current_standard.json          # Current winning config
└── results/
    └── trial_*_result.json        # Evaluation results
```

## CERATA Evolution Cycle

```
1. HUNT     → Find new prey (external repositories)
2. EXTRACT  → Clone nematocysts (useful patterns)
3. ADAPT    → Modify for Rose Glass integration
4. TRIAL    → Test experimental vs classic (YOU ARE HERE)
5. EVALUATE → Measure fitness, determine winner
6. PROMOTE  → Winner becomes new standard
7. GRAVEYARD→ Loser feeds nutrients for next hunt
```

## Best Practices

1. **Always define clear success criteria** before starting trial
2. **Use 50/50 split** unless you have reason for different allocation
3. **Wait for min_sample_size** before evaluating (statistical validity)
4. **Track relevant metrics** for your trial type (map to TrialBranch fields)
5. **Document learnings** from both winners and losers
6. **Promote winners promptly** to avoid drift from standard
7. **Archive losers with rationale** to feed future experiments

## Future Trials

**Planned**:
- ML Lead Scoring (scikit-learn/XGBoost vs rule-based)
- AI Agent Qualification (LangChain agents vs manual)
- Multi-Modal Extraction (Vision + Text vs Text-only)
- Distributed Hunting (Celery workers vs single process)

**Ideas from Graveyard**:
- Weighted lens experiments
- Authority-heavy vs intent-heavy scoring
- Temporal decay models
- Graph-based lead relationships

---

🌹 **Rose Glass sees all, judges none, learns always**
