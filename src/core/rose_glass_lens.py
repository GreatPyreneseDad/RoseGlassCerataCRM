"""
Rose Glass CRM Lens - Lead Coherence Perception
================================================

Translates lead signals into perceivable patterns for sales qualification.

Dimensions (adapted for CRM):
- Ψ (psi): Intent Coherence - Does their need match our solution?
- ρ (rho): Depth/Authority - Decision-making capacity and budget signals
- q: Urgency/Activation - Buying timeline and pain intensity
- f: Fit/Belonging - ICP alignment and ecosystem compatibility
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib


@dataclass
class LeadCoherence:
    """Result of perceiving a lead through Rose Glass"""
    
    # Core dimensions (0-1 scale)
    psi_intent: float       # Intent coherence - need/solution match
    rho_authority: float    # Depth - decision power and budget
    q_urgency: float        # Activation - timeline and pain level
    f_fit: float            # Belonging - ICP and ecosystem fit
    
    # Derived metrics
    coherence_score: float  # Overall lead quality (0-4)
    qualification_tier: str # 'hot', 'warm', 'cold', 'disqualified'
    
    # Metadata
    lens_used: str          # Which industry lens
    timestamp: datetime
    confidence: float       # How certain is this reading?
    
    # Signals detected
    positive_signals: List[str] = field(default_factory=list)
    warning_signals: List[str] = field(default_factory=list)
    disqualifiers: List[str] = field(default_factory=list)
    
    # Recommended actions
    next_actions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dimensions': {
                'psi_intent': round(self.psi_intent, 3),
                'rho_authority': round(self.rho_authority, 3),
                'q_urgency': round(self.q_urgency, 3),
                'f_fit': round(self.f_fit, 3),
            },
            'coherence_score': round(self.coherence_score, 3),
            'qualification_tier': self.qualification_tier,
            'lens_used': self.lens_used,
            'timestamp': self.timestamp.isoformat(),
            'confidence': round(self.confidence, 3),
            'signals': {
                'positive': self.positive_signals,
                'warning': self.warning_signals,
                'disqualifiers': self.disqualifiers,
            },
            'next_actions': self.next_actions,
        }


@dataclass
class LeadData:
    """Raw lead data for perception"""
    
    # Identity
    lead_id: str
    company_name: str
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None
    
    # Company signals
    industry: Optional[str] = None
    company_size: Optional[str] = None
    revenue_range: Optional[str] = None
    tech_stack: List[str] = field(default_factory=list)
    
    # Intent signals
    source: str = 'unknown'
    initial_interest: Optional[str] = None
    pain_points: List[str] = field(default_factory=list)
    
    # Authority signals
    is_decision_maker: Optional[bool] = None
    budget_mentioned: Optional[bool] = None
    timeline_mentioned: Optional[str] = None
    
    # Fit signals
    current_solution: Optional[str] = None
    competitor_mentioned: List[str] = field(default_factory=list)
    use_case: Optional[str] = None
    
    # Engagement signals
    website_visits: int = 0
    content_downloads: List[str] = field(default_factory=list)
    email_opens: int = 0
    meeting_requests: int = 0
    
    # Raw text for analysis
    notes: str = ''
    email_content: str = ''
    call_transcript: str = ''
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_text_for_analysis(self) -> str:
        """Combine all text fields for Rose Glass analysis"""
        parts = [
            self.notes,
            self.email_content,
            self.call_transcript,
            self.initial_interest or '',
            ' '.join(self.pain_points),
            self.use_case or '',
        ]
        return ' '.join(p for p in parts if p)


class RoseGlassCRMLens:
    """
    Perceives lead quality through Rose Glass dimensions.
    
    NOT a scoring system - a translation lens that makes
    lead patterns visible to synthetic intelligence.
    """
    
    # Biological optimization constants
    KM = 0.2
    KI = 0.8
    
    DEFAULT_WEIGHTS = {
        'psi_intent': 0.25,
        'rho_authority': 0.30,
        'q_urgency': 0.25,
        'f_fit': 0.20,
    }
    
    LENS_CALIBRATIONS = {
        'enterprise_saas': {
            'weights': {'psi_intent': 0.20, 'rho_authority': 0.35, 'q_urgency': 0.20, 'f_fit': 0.25},
            'authority_threshold': 0.6,
        },
        'smb_tech': {
            'weights': {'psi_intent': 0.30, 'rho_authority': 0.20, 'q_urgency': 0.30, 'f_fit': 0.20},
            'authority_threshold': 0.4,
        },
        'federal_gov': {
            'weights': {'psi_intent': 0.25, 'rho_authority': 0.25, 'q_urgency': 0.15, 'f_fit': 0.35},
            'authority_threshold': 0.5,
        },
        'healthcare': {
            'weights': {'psi_intent': 0.20, 'rho_authority': 0.30, 'q_urgency': 0.20, 'f_fit': 0.30},
            'authority_threshold': 0.55,
        },
    }
    
    def __init__(self, lens_name: str = 'enterprise_saas'):
        self.lens_name = lens_name
        self.calibration = self.LENS_CALIBRATIONS.get(lens_name, {})
        self.weights = self.calibration.get('weights', self.DEFAULT_WEIGHTS)
    
    def biological_optimization(self, q_raw: float) -> float:
        """Apply Michaelis-Menten kinetics to urgency"""
        if q_raw <= 0:
            return 0.0
        return q_raw / (self.KM + q_raw + (q_raw**2 / self.KI))
    
    def perceive(self, lead: LeadData) -> LeadCoherence:
        """Perceive a lead through the Rose Glass"""
        psi = self._extract_psi_intent(lead)
        rho = self._extract_rho_authority(lead)
        q_raw = self._extract_q_urgency(lead)
        f = self._extract_f_fit(lead)
        
        q = self.biological_optimization(q_raw)
        coherence = self._calculate_coherence(psi, rho, q, f)
        tier = self._determine_tier(coherence, psi, rho, q, f)
        positive, warning, disqualifiers = self._detect_signals(lead, psi, rho, q, f)
        actions = self._recommend_actions(tier, lead, psi, rho, q, f)
        confidence = self._calculate_confidence(lead)
        
        return LeadCoherence(
            psi_intent=psi,
            rho_authority=rho,
            q_urgency=q,
            f_fit=f,
            coherence_score=coherence,
            qualification_tier=tier,
            lens_used=self.lens_name,
            timestamp=datetime.now(),
            confidence=confidence,
            positive_signals=positive,
            warning_signals=warning,
            disqualifiers=disqualifiers,
            next_actions=actions,
        )
    
    def _extract_psi_intent(self, lead: LeadData) -> float:
        """Extract Ψ - Intent Coherence"""
        score = 0.0
        
        source_weights = {
            'inbound': 0.3, 'referral': 0.25, 'event': 0.2,
            'content': 0.15, 'outbound': 0.1, 'unknown': 0.05
        }
        score += source_weights.get(lead.source, 0.05)
        
        if lead.pain_points:
            score += min(len(lead.pain_points) * 0.1, 0.3)
        
        if lead.use_case:
            score += 0.2
        
        if lead.meeting_requests > 0:
            score += 0.15
        if lead.content_downloads:
            score += min(len(lead.content_downloads) * 0.05, 0.15)
        
        return min(score, 1.0)
    
    def _extract_rho_authority(self, lead: LeadData) -> float:
        """Extract ρ - Decision Authority"""
        score = 0.0
        
        if lead.is_decision_maker:
            score += 0.35
        elif lead.is_decision_maker is None:
            score += 0.15
        
        authority_titles = ['ceo', 'cto', 'cfo', 'coo', 'vp', 'director', 'head of', 'chief']
        if lead.contact_title:
            title_lower = lead.contact_title.lower()
            if any(t in title_lower for t in authority_titles):
                score += 0.25
        
        if lead.budget_mentioned:
            score += 0.2
        
        size_weights = {
            'enterprise': 0.15, 'mid-market': 0.2,
            'smb': 0.15, 'startup': 0.1
        }
        score += size_weights.get(lead.company_size or '', 0.1)
        
        return min(score, 1.0)
    
    def _extract_q_urgency(self, lead: LeadData) -> float:
        """Extract q - Urgency/Activation Energy"""
        score = 0.0
        
        if lead.timeline_mentioned:
            timeline_weights = {
                'immediate': 0.4, 'this_quarter': 0.3,
                'next_quarter': 0.2, 'this_year': 0.1
            }
            score += timeline_weights.get(lead.timeline_mentioned, 0.1)
        
        text = lead.get_text_for_analysis().lower()
        urgency_markers = [
            'urgent', 'asap', 'immediately', 'critical', 'deadline',
            'struggling', 'failing', 'breaking', 'desperate', 'need now'
        ]
        urgency_count = sum(1 for m in urgency_markers if m in text)
        score += min(urgency_count * 0.1, 0.3)
        
        if lead.meeting_requests > 1:
            score += 0.15
        if lead.website_visits > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_f_fit(self, lead: LeadData) -> float:
        """Extract f - ICP Fit / Ecosystem Belonging"""
        score = 0.0
        
        target_industries = ['technology', 'saas', 'software', 'fintech', 'healthcare tech']
        if lead.industry and any(t in lead.industry.lower() for t in target_industries):
            score += 0.25
        
        if lead.tech_stack:
            score += min(len(lead.tech_stack) * 0.05, 0.2)
        
        if lead.company_size in ['mid-market', 'enterprise']:
            score += 0.2
        elif lead.company_size == 'smb':
            score += 0.15
        
        if not lead.competitor_mentioned:
            score += 0.15
        elif lead.competitor_mentioned:
            score += 0.1
        
        if lead.source == 'referral':
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_coherence(self, psi: float, rho: float, q: float, f: float) -> float:
        """Calculate overall coherence score"""
        coupling_strength = 0.15
        coupling = coupling_strength * rho * psi
        
        coherence = (
            self.weights['psi_intent'] * psi +
            self.weights['rho_authority'] * rho +
            self.weights['q_urgency'] * q +
            self.weights['f_fit'] * f +
            coupling
        ) * 4
        
        return min(coherence, 4.0)
    
    def _determine_tier(self, coherence: float, psi: float, rho: float, 
                       q: float, f: float) -> str:
        """Determine qualification tier"""
        authority_threshold = self.calibration.get('authority_threshold', 0.5)
        
        if f < 0.2:
            return 'disqualified'
        if rho < 0.15:
            return 'disqualified'
        
        if coherence >= 2.5 and rho >= authority_threshold and q >= 0.3:
            return 'hot'
        
        if coherence >= 1.5:
            return 'warm'
        
        return 'cold'
    
    def _detect_signals(self, lead: LeadData, psi: float, rho: float,
                       q: float, f: float) -> tuple:
        """Detect positive, warning, and disqualifying signals"""
        positive = []
        warning = []
        disqualifiers = []
        
        if psi >= 0.6:
            positive.append('Strong intent signals')
        if rho >= 0.6:
            positive.append('Decision-making authority')
        if q >= 0.5:
            positive.append('Urgency expressed')
        if f >= 0.6:
            positive.append('Strong ICP fit')
        if lead.source == 'referral':
            positive.append('Referral lead (ecosystem validated)')
        if lead.budget_mentioned:
            positive.append('Budget discussed')
        
        if rho < 0.4 and psi > 0.5:
            warning.append('Intent without authority - may need champion')
        if q > 0.7 and rho < 0.4:
            warning.append('High urgency + low authority - may be researcher')
        if lead.competitor_mentioned:
            warning.append(f'Currently using: {", ".join(lead.competitor_mentioned)}')
        if psi < 0.3:
            warning.append('Unclear intent - needs discovery')
        
        if f < 0.2:
            disqualifiers.append('Poor ICP fit')
        if rho < 0.15 and lead.company_size == 'enterprise':
            disqualifiers.append('Too junior for enterprise deal')
        
        return positive, warning, disqualifiers
    
    def _recommend_actions(self, tier: str, lead: LeadData, 
                          psi: float, rho: float, q: float, f: float) -> List[str]:
        """Recommend next actions based on lead state"""
        actions = []
        
        if tier == 'disqualified':
            actions.append('Archive - does not meet qualification criteria')
            return actions
        
        if tier == 'hot':
            actions.append('Schedule demo/meeting ASAP')
            if not lead.budget_mentioned:
                actions.append('Confirm budget in first call')
            if q >= 0.6:
                actions.append('Offer accelerated timeline')
        
        elif tier == 'warm':
            if psi < 0.5:
                actions.append('Discovery call to understand needs')
            if rho < 0.5:
                actions.append('Identify decision-maker / champion')
            if q < 0.3:
                actions.append('Create urgency - share ROI data')
            actions.append('Add to nurture sequence')
        
        elif tier == 'cold':
            actions.append('Add to long-term nurture')
            if psi < 0.3:
                actions.append('Send educational content')
            actions.append('Re-evaluate in 30 days')
        
        return actions
    
    def _calculate_confidence(self, lead: LeadData) -> float:
        """Calculate confidence based on data completeness"""
        data_points = 0
        max_points = 10
        
        if lead.contact_name:
            data_points += 1
        if lead.contact_title:
            data_points += 1
        if lead.industry:
            data_points += 1
        if lead.company_size:
            data_points += 1
        if lead.pain_points:
            data_points += 1
        if lead.is_decision_maker is not None:
            data_points += 1
        if lead.budget_mentioned is not None:
            data_points += 1
        if lead.timeline_mentioned:
            data_points += 1
        if lead.get_text_for_analysis().strip():
            data_points += 2
        
        return data_points / max_points
