# Team Recovery - Rose Glass CRM

**Customized for**: Team Recovery, Draper, Utah
**Purpose**: Behavioral health admissions qualification with crisis detection

## Quick Start

### Installation (One-Time Setup)

```bash
# Navigate to project directory
cd ~/Documents/RoseGlassCerataCRM

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Test installation
python3 team_recovery/add_phone_inquiry.py
```

### Daily Usage

#### Phone Inquiry Entry

When someone calls:

```bash
python3 team_recovery/add_phone_inquiry.py
```

Follow the prompts to enter:
1. Contact information (name, phone, email)
2. Referral source (self, family, court, etc.)
3. Clinical information (substances, previous treatment)
4. Insurance/resources
5. Urgency assessment
6. Additional notes

**System will immediately**:
- Calculate Rose Glass coherence score
- Assign qualification tier (CRISIS/HOT/WARM/COLD/NOT READY)
- Flag crisis situations
- Recommend next actions
- Save to pending admissions

#### Crisis Protocol

If system displays 🚨 **CRISIS ALERT**:

1. **STOP** - Do not continue with normal workflow
2. **Contact crisis clinician immediately**
3. **Clinical assessment required within 2 hours**
4. **Have crisis resources ready**:
   - National Suicide Prevention: **988**
   - Medical emergency: **911**
   - Team Recovery crisis line: **[Your Crisis Line]**
5. **Document** all interventions

## Qualification Tiers

### CRISIS (q > 0.7)
**Indicators**: Suicide risk, overdose, severe withdrawal, immediate danger
**Action**: Clinical assessment NOW (< 2 hours)
**Priority**: IMMEDIATE

### HOT (C ≥ 2.5)
**Indicators**: Ready, has resources, urgent timeline
**Action**: Admission within 24-48 hours
**Priority**: HIGH
**Follow-up**:
- Verify insurance within 4 hours
- Schedule clinical assessment today
- Bed assignment ASAP

### WARM (C ≥ 1.5)
**Indicators**: Interested, needs verification
**Action**: Insurance inquiry, assessment scheduled
**Priority**: MEDIUM
**Follow-up**:
- Send insurance verification
- Follow-up call in 3 days
- Educational materials

### COLD (C < 1.5)
**Indicators**: Early inquiry, exploring
**Action**: Long-term nurture
**Priority**: LOW
**Follow-up**:
- Educational email sequence
- Monthly check-in
- Re-evaluate in 30 days

### NOT READY (C < 0.5)
**Indicators**: Poor fit, no resources, not appropriate
**Action**: Referral to other resources
**Priority**: ARCHIVE

## Understanding Rose Glass Dimensions

**Ψ (Psi) - Readiness**: How motivated is the person?
- Self-referred (high) vs. court-ordered (lower)
- Expressed desire for help
- Previous treatment attempts show pattern

**ρ (Rho) - Resources**: Can they access treatment?
- Insurance verified/pending
- Family support
- Financial capacity

**q - Urgency**: How quickly do they need help?
- **> 0.7**: CRISIS (immediate safety concern)
- **0.4-0.7**: High urgency (this week)
- **< 0.4**: Normal timeline

**f - Fit**: Does our program match their needs?
- Substance matches our specialties
- Age/demographics appropriate
- Co-occurring disorders we can treat

## File Structure

```
team_recovery/
├── README.md                    # This file
├── add_phone_inquiry.py        # Interactive lead entry
└── [Future scripts]
    ├── daily_processing.py     # Process yesterday's leads
    ├── weekly_report.py        # Weekly metrics
    └── record_outcome.py       # Track admissions/outcomes

data/
└── leads/
    └── pending_admissions.json  # All pending leads

config/lenses/
└── team_recovery_draper.yaml   # Recovery-specific calibration
```

## Privacy & Compliance

### HIPAA Requirements

⚠️ **IMPORTANT**: All lead data contains PHI (Protected Health Information)

**Required Security**:
- [ ] Data stored on encrypted drive
- [ ] Access limited to admissions team
- [ ] Never email lead data (use secure portal)
- [ ] Audit all access
- [ ] Document retention: 7 years

**Encryption Setup (macOS)**:
```bash
# Create encrypted volume for data
diskutil apfs addVolume disk1 APFS "TeamRecovery-PHI" -encryption
```

### Legal Disclaimer

Rose Glass CRM is a **qualification tool**, not clinical assessment.

- System flags urgency - clinician makes diagnosis
- `q > 0.7` = flag for review, not a diagnosis
- Licensed clinician MUST assess all crisis flags
- Clinical judgment always overrides system

## Training (30 Minutes)

### For New Admissions Staff

**Session Plan**:
1. Concept (5 min): Watch rose glass demo
2. Practice (10 min): Enter 3 sample cases
3. Workflow (10 min): Morning routine, crisis protocol
4. Q&A (5 min)

**Sample Practice Cases**:

**Case 1 - HOT Lead**:
- Name: John Smith
- Source: Self-referral
- Substance: Alcohol, 15 years
- Insurance: Blue Cross verified
- Timeline: This week
- Notes: "I'm done, need help now"

**Case 2 - CRISIS**:
- Name: Sarah Johnson
- Source: ER referral
- Substance: Opioids
- Insurance: Medicaid
- Timeline: Immediate
- Notes: "Overdosed yesterday, suicidal ideation"

**Case 3 - WARM Lead**:
- Name: Mike Davis
- Source: Family referral
- Substance: Stimulants
- Insurance: Pending verification
- Timeline: This month
- Notes: "Wife called, he's resistant but agreed to consider"

## Troubleshooting

### Common Issues

**Q**: System says "Crisis" but person seems stable
**A**: Review notes for crisis keywords. System is conservative. Clinical assessment still required - better safe than sorry.

**Q**: Insurance verified but system says low authority
**A**: Check `rho_authority` calculation. May need to update lens weights if this happens frequently.

**Q**: Too many "NOT READY" - losing good leads?
**A**: Review disqualification criteria in `team_recovery_draper.yaml`. May need to lower threshold.

**Q**: Script won't run / errors
**A**:
1. Check virtual environment is activated
2. Verify Python path: `which python3`
3. Reinstall dependencies: `pip install -r requirements.txt`
4. Contact technical support

## Support

**Technical Issues**: Create issue at https://github.com/GreatPyreneseDad/RoseGlassCerataCRM/issues

**Clinical Questions**: Contact Team Recovery clinical director

**System Updates**: Check GitHub repository for latest version

## Success Metrics

### Week 1 Goals
- [ ] All admissions staff trained
- [ ] 25+ leads entered
- [ ] Crisis protocol tested
- [ ] Team comfort: 4/5 rating

### Month 1 Goals
- [ ] 100+ leads qualified
- [ ] Baseline conversion rate established
- [ ] Crisis detection: 100% reviewed within 2 hours
- [ ] Hot lead time-to-admission: < 48 hours

### Month 3 Goals
- [ ] First trial completed
- [ ] Graveyard insights: 3+ patterns identified
- [ ] Improved qualification accuracy
- [ ] CRM integration (if needed)

---

**Remember**: Rose Glass **enhances** clinical judgment, it doesn't replace it.

🌹 *Rose Glass sees all, judges none, learns always*
