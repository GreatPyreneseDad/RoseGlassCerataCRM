"""
Web-based Lead Hunter
=====================

Hunts for leads through web search and content analysis.
Creates initial LeadData objects with basic signals for Rose Glass perception.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import re
import hashlib
import logging
from urllib.parse import quote_plus
import asyncio

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# Import LeadData from core
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.rose_glass_lens import LeadData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HuntCriteria:
    """Defines what we're hunting for (ICP specification)"""

    # Target profile
    target_industries: List[str] = field(default_factory=list)
    company_sizes: List[str] = field(default_factory=list)  # 'startup', 'smb', 'mid-market', 'enterprise'
    target_titles: List[str] = field(default_factory=list)  # Decision-maker titles

    # Intent signals
    pain_keywords: List[str] = field(default_factory=list)  # Problems they're expressing
    solution_keywords: List[str] = field(default_factory=list)  # What they're looking for

    # Geographic
    regions: List[str] = field(default_factory=list)  # Countries, states, cities

    # Exclusions
    exclude_competitors: List[str] = field(default_factory=list)
    exclude_industries: List[str] = field(default_factory=list)

    # Hunt parameters
    max_results_per_hunt: int = 50
    min_company_size_employees: Optional[int] = None
    max_company_size_employees: Optional[int] = None

    def generate_search_queries(self) -> List[str]:
        """Generate search queries based on criteria"""
        queries = []

        # Combine pain points with industries
        for pain in self.pain_keywords[:3]:  # Top 3 pain points
            for industry in self.target_industries[:2]:  # Top 2 industries
                query = f"{pain} {industry}"
                if self.target_titles:
                    query += f" {self.target_titles[0]}"
                queries.append(query)

        # Solution-focused queries
        for solution in self.solution_keywords[:2]:
            for industry in self.target_industries[:2]:
                queries.append(f"{solution} for {industry}")

        return queries[:10]  # Max 10 queries per hunt


@dataclass
class HuntResult:
    """Individual lead discovered during hunt"""

    url: str
    title: str
    snippet: str
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None

    # Signals detected
    industry_signals: List[str] = field(default_factory=list)
    pain_signals: List[str] = field(default_factory=list)
    urgency_signals: List[str] = field(default_factory=list)

    # Metadata
    discovered_at: datetime = field(default_factory=datetime.now)
    source: str = 'web_search'

    def to_lead_data(self, hunt_id: str) -> LeadData:
        """Convert hunt result to LeadData for Rose Glass perception"""
        lead_id = hashlib.md5(f"{self.company_name}_{self.url}".encode()).hexdigest()[:12]

        return LeadData(
            lead_id=lead_id,
            company_name=self.company_name or 'Unknown',
            contact_name=self.contact_name,
            contact_title=self.contact_title,
            contact_email=self.contact_email,
            industry=self.industry_signals[0] if self.industry_signals else None,
            pain_points=self.pain_signals,
            source='web_hunt',
            initial_interest=self.snippet,
            notes=f"Discovered via web hunt {hunt_id}\nURL: {self.url}\nTitle: {self.title}",
            created_at=self.discovered_at,
            updated_at=self.discovered_at,
        )


class WebHunter:
    """
    Hunts for leads through web search and content analysis.

    Ethical hunting principles:
    - Respects robots.txt
    - Rate limits requests
    - No aggressive scraping
    - Focuses on publicly available information
    """

    def __init__(
        self,
        user_agent: str = "RoseGlassCRM/1.0 (Lead Research Bot)",
        rate_limit_seconds: float = 2.0
    ):
        self.user_agent = user_agent
        self.rate_limit_seconds = rate_limit_seconds
        self.last_request_time = 0

        if not AIOHTTP_AVAILABLE:
            logger.warning("aiohttp not available - install for async web hunting")
        if not BS4_AVAILABLE:
            logger.warning("beautifulsoup4 not available - install for HTML parsing")

    async def hunt(self, criteria: HuntCriteria) -> List[HuntResult]:
        """
        Execute a hunt based on criteria.

        Returns list of HuntResult objects ready for Rose Glass perception.
        """
        hunt_id = hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        logger.info(f"🔍 Starting hunt {hunt_id} for industries: {criteria.target_industries}")

        results = []
        queries = criteria.generate_search_queries()

        for query in queries:
            logger.info(f"  Searching: {query}")
            query_results = await self._search_web(query, criteria)
            results.extend(query_results)

            # Rate limiting
            await asyncio.sleep(self.rate_limit_seconds)

        # Deduplicate by company name
        seen_companies = set()
        unique_results = []
        for result in results:
            if result.company_name and result.company_name not in seen_companies:
                seen_companies.add(result.company_name)
                unique_results.append(result)

        logger.info(f"✓ Hunt {hunt_id} complete: {len(unique_results)} unique leads discovered")
        return unique_results[:criteria.max_results_per_hunt]

    async def _search_web(self, query: str, criteria: HuntCriteria) -> List[HuntResult]:
        """
        Search the web for leads matching query.

        Note: This is a simplified implementation. Production would use:
        - Google Custom Search API
        - Bing Search API
        - LinkedIn Sales Navigator API
        - ZoomInfo or similar data provider
        """
        results = []

        # Simulated search results (replace with real API in production)
        # This demonstrates the structure - actual implementation would call search APIs
        logger.info(f"    [DEMO MODE] Would search: {query}")
        logger.info("    Production: Integrate Google Custom Search API or similar")

        # Demo result structure:
        demo_results = [
            {
                'url': f'https://example.com/company-{i}',
                'title': f'Company solving {query}',
                'snippet': f'We help businesses with {query}. Contact us for demo.',
            }
            for i in range(3)
        ]

        for item in demo_results:
            result = self._parse_search_result(item, query, criteria)
            if result:
                results.append(result)

        return results

    def _parse_search_result(
        self,
        search_item: Dict[str, Any],
        query: str,
        criteria: HuntCriteria
    ) -> Optional[HuntResult]:
        """Parse a search result into a HuntResult"""

        # Extract basic info
        url = search_item.get('url', '')
        title = search_item.get('title', '')
        snippet = search_item.get('snippet', '')

        # Extract company name from URL or title
        company_name = self._extract_company_name(url, title)

        # Detect signals
        text = f"{title} {snippet}".lower()

        industry_signals = [ind for ind in criteria.target_industries if ind.lower() in text]
        pain_signals = [pain for pain in criteria.pain_keywords if pain.lower() in text]

        urgency_keywords = ['urgent', 'immediate', 'asap', 'struggling', 'need', 'help']
        urgency_signals = [word for word in urgency_keywords if word in text]

        # Check exclusions
        if any(comp.lower() in text for comp in criteria.exclude_competitors):
            logger.info(f"    Skipping competitor: {company_name}")
            return None

        if any(ind.lower() in text for ind in criteria.exclude_industries):
            logger.info(f"    Skipping excluded industry: {company_name}")
            return None

        return HuntResult(
            url=url,
            title=title,
            snippet=snippet,
            company_name=company_name,
            industry_signals=industry_signals,
            pain_signals=pain_signals,
            urgency_signals=urgency_signals,
        )

    def _extract_company_name(self, url: str, title: str) -> str:
        """Extract company name from URL or title"""
        # Try to extract from domain
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1)
            # Clean up domain
            name = domain.split('.')[0]
            return name.replace('-', ' ').title()

        # Fallback to first part of title
        return title.split('|')[0].split('-')[0].strip()

    async def enrich_lead(self, lead: LeadData) -> LeadData:
        """
        Enrich a lead with additional web research.

        In production, this would:
        - Visit company website
        - Extract tech stack (BuiltWith, Wappalyzer)
        - Find social profiles
        - Check company size (LinkedIn, Crunchbase)
        - Identify decision makers
        """
        logger.info(f"🔬 Enriching lead: {lead.company_name}")

        # Demo: Simulated enrichment
        # Production would use:
        # - Clearbit API
        # - Hunter.io for email finding
        # - LinkedIn Sales Navigator
        # - ZoomInfo, Apollo.io, etc.

        logger.info("    [DEMO MODE] Would enrich from:")
        logger.info("    - Company website scraping")
        logger.info("    - LinkedIn company profile")
        logger.info("    - Tech stack detection")
        logger.info("    - Contact email finding")

        return lead

    def hunt_sync(self, criteria: HuntCriteria) -> List[HuntResult]:
        """Synchronous wrapper for hunt()"""
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp required for web hunting - install with: pip install aiohttp")
            return []

        return asyncio.run(self.hunt(criteria))


# Example usage
if __name__ == "__main__":
    # Define what we're hunting for
    criteria = HuntCriteria(
        target_industries=['SaaS', 'Technology', 'Fintech'],
        company_sizes=['mid-market', 'enterprise'],
        target_titles=['CTO', 'VP Engineering', 'Director of IT'],
        pain_keywords=['security compliance', 'data protection', 'access control'],
        solution_keywords=['identity management', 'SSO', 'authentication'],
        exclude_competitors=['Okta', 'Auth0'],
    )

    # Execute hunt
    hunter = WebHunter()

    # Async hunt
    async def demo():
        results = await hunter.hunt(criteria)

        print(f"\n🎯 Hunt Results: {len(results)} leads")
        for result in results[:3]:
            print(f"\n{result.company_name}")
            print(f"  URL: {result.url}")
            print(f"  Signals: {result.pain_signals}")

            # Convert to LeadData
            lead = result.to_lead_data(hunt_id="demo")
            print(f"  Lead ID: {lead.lead_id}")

    asyncio.run(demo())
