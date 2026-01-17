#!/usr/bin/env python3
"""
Team Recovery - Quick Phone Inquiry Entry
==========================================

Interactive script for admissions team to quickly enter phone inquiries
and get immediate Rose Glass qualification.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from hunter.data_hunter import DataHunter
from pipeline.qualifier import LeadQualifier


def add_phone_inquiry():
    """Interactive lead entry for phone inquiries"""

    print("\n" + "=" * 70)
    print("  TEAM RECOVERY - PHONE INQUIRY ENTRY")
    print("  Draper, Utah")
    print("=" * 70)

    # Collect information
    print("\n--- CONTACT INFORMATION ---")
    name = input("Full Name: ").strip()
    if not name:
        print("Error: Name is required")
        return

    phone = input("Phone: ").strip()
    email = input("Email (optional): ").strip() or None

    print("\n--- REFERRAL SOURCE ---")
    print("  1. Self (individual called)")
    print("  2. Family member")
    print("  3. Therapist/Provider")
    print("  4. Court/Legal system")
    print("  5. ER/Hospital")
    print("  6. Friend/Peer")
    print("  7. Employer/EAP")
    print("  8. Other")

    source_map = {
        '1': 'self_referral',
        '2': 'family_referral',
        '3': 'therapist_referral',
        '4': 'court_ordered',
        '5': 'er_referral',
        '6': 'friend_referral',
        '7': 'employer_referral',
        '8': 'unknown',
    }
    source_choice = input("Select (1-8): ").strip()
    source = source_map.get(source_choice, 'unknown')

    # Substance information
    print("\n--- CLINICAL INFORMATION ---")
    substance = input("Primary substance of concern: ").strip()
    substances = [substance] if substance else []

    secondary = input("Secondary substance (optional): ").strip()
    if secondary:
        substances.append(secondary)

    previous_treatment = input("Previous treatment? (y/n): ").strip().lower() == 'y'

    # Insurance/resources
    print("\n--- INSURANCE & RESOURCES ---")
    print("  1. Private insurance")
    print("  2. Medicaid")
    print("  3. Medicare")
    print("  4. Tricare (military)")
    print("  5. Self-pay")
    print("  6. No insurance/unsure")

    insurance_map = {
        '1': 'private_insurance',
        '2': 'medicaid',
        '3': 'medicare',
        '4': 'tricare',
        '5': 'self_pay',
        '6': 'uninsured',
    }
    insurance_choice = input("Select (1-6): ").strip()
    insurance_type = insurance_map.get(insurance_choice, 'uninsured')

    if insurance_choice in ['1', '2', '3', '4']:
        insurance_provider = input("  Provider name: ").strip()
    else:
        insurance_provider = insurance_type

    # Urgency assessment
    print("\n--- URGENCY ASSESSMENT ---")
    print("⚠️  CRISIS INDICATORS:")
    crisis_check = input("Any suicide risk, overdose, severe withdrawal? (y/n): ").strip().lower()

    if crisis_check == 'y':
        print("\n🚨 CRISIS PROTOCOL:")
        print("  1. IMMEDIATE clinical assessment required")
        print("  2. Contact crisis clinician NOW")
        print("  3. National Suicide Prevention: 988")
        print("  4. If medical emergency: 911")
        timeline = 'immediate'
        crisis_flag = True
    else:
        crisis_flag = False
        print("\nWhen are they looking to start?")
        print("  1. Immediately (today/tomorrow)")
        print("  2. This week")
        print("  3. This month")
        print("  4. Next month")
        print("  5. Just exploring options")

        timeline_map = {
            '1': 'immediate',
            '2': 'this_week',
            '3': 'this_month',
            '4': 'next_month',
            '5': 'exploring',
        }
        timeline_choice = input("Select (1-5): ").strip()
        timeline = timeline_map.get(timeline_choice, 'exploring')

    # Additional notes
    print("\n--- ADDITIONAL NOTES ---")
    notes = input("Any additional information: ").strip()

    # Create lead
    print("\n🔍 Analyzing lead through Rose Glass...")

    hunter = DataHunter()
    lead = hunter.create_manual_lead(
        company_name=name,  # For individuals, use name as identifier
        contact_name=name,
        contact_email=email,
        contact_title='client',
        industry='recovery_services',
        company_size='individual',
        pain_points=substances,
        source=source,
        timeline_mentioned=timeline,
        notes=f"Phone inquiry. Insurance: {insurance_provider}. {notes}",
        # Additional fields (stored in notes for now)
    )

    # Add recovery-specific data to notes
    recovery_data = {
        'phone': phone,
        'substances': substances,
        'previous_treatment': previous_treatment,
        'insurance_type': insurance_type,
        'insurance_provider': insurance_provider,
        'crisis_flag': crisis_flag,
    }
    lead.notes += f"\n\nRecovery Data: {json.dumps(recovery_data, indent=2)}"

    # Qualify through Team Recovery lens
    try:
        qualifier = LeadQualifier(lens_name='team_recovery_draper', trial_branch='classic')
        result = qualifier.qualify(lead)
    except Exception as e:
        print(f"\n❌ Error during qualification: {e}")
        print("Defaulting to manual triage")
        return

    # Display result
    print("\n" + "=" * 70)
    print("  ROSE GLASS QUALIFICATION RESULT")
    print("=" * 70)

    # Crisis alert
    if result.coherence.q_urgency > 0.7 or crisis_flag:
        print("\n🚨 🚨 🚨 CRISIS ALERT 🚨 🚨 🚨")
        print("\n  IMMEDIATE ACTION REQUIRED:")
        print("  1. Contact crisis clinician NOW")
        print("  2. Clinical assessment within 2 hours")
        print("  3. Document all interventions")
        print("  4. Suicide Prevention Lifeline: 988")
        print("\n" + "=" * 70)

    # Qualification details
    print(f"\nLead: {name}")
    print(f"Tier: {result.qualification_tier.upper()}")
    print(f"Coherence Score: {result.coherence.coherence_score:.2f} / 4.0")
    print(f"Priority: {result.priority_score:.2f}")

    print(f"\nDimensions:")
    print(f"  Ψ (Readiness):  {result.coherence.psi_intent:.2f}")
    print(f"  ρ (Resources):  {result.coherence.rho_authority:.2f}")
    print(f"  q (Urgency):    {result.coherence.q_urgency:.2f}")
    print(f"  f (Program Fit): {result.coherence.f_fit:.2f}")

    if result.coherence.positive_signals:
        print(f"\n✓ Positive Signals:")
        for signal in result.coherence.positive_signals:
            print(f"  • {signal}")

    if result.coherence.warning_signals:
        print(f"\n⚠️  Warnings:")
        for warning in result.coherence.warning_signals:
            print(f"  • {warning}")

    print(f"\n📋 Next Actions:")
    for action in result.coherence.next_actions:
        print(f"  • {action}")

    print(f"\nNext Stage: {result.next_stage}")

    # Save option
    print("\n" + "=" * 70)
    save = input("\nSave lead to pending admissions? (y/n): ").strip().lower()

    if save == 'y':
        # Save to pending admissions file
        pending_file = Path(__file__).parent.parent / 'data' / 'leads' / 'pending_admissions.json'
        pending_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing
        if pending_file.exists():
            with open(pending_file) as f:
                pending = json.load(f)
        else:
            pending = []

        # Add new lead
        lead_entry = {
            'lead_id': lead.lead_id,
            'name': name,
            'phone': phone,
            'email': email,
            'source': source,
            'substances': substances,
            'insurance_provider': insurance_provider,
            'insurance_type': insurance_type,
            'timeline': timeline,
            'crisis_flag': crisis_flag,
            'notes': notes,
            'qualification': result.to_dict(),
            'entered_at': datetime.now().isoformat(),
            'entered_by': 'admissions',
        }

        pending.append(lead_entry)

        # Save
        with open(pending_file, 'w') as f:
            json.dump(pending, f, indent=2)

        print(f"\n✓ Lead saved!")
        print(f"  Lead ID: {lead.lead_id}")
        print(f"  Tier: {result.qualification_tier.upper()}")
        print(f"  File: {pending_file}")

        # Create follow-up reminder
        if result.qualification_tier == 'hot':
            print(f"\n⏰ FOLLOW-UP REMINDER:")
            print(f"  • Verify insurance within 4 hours")
            print(f"  • Schedule clinical assessment within 24 hours")
            print(f"  • Goal: Admission within 48 hours")
        elif result.qualification_tier == 'warm':
            print(f"\n⏰ FOLLOW-UP REMINDER:")
            print(f"  • Send insurance verification inquiry")
            print(f"  • Follow-up call in 3 business days")

    else:
        print("\n Lead not saved")

    print("\n" + "=" * 70)
    print("  Thank you for using Rose Glass CRM")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        add_phone_inquiry()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
