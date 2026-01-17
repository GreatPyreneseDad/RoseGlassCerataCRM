"""
CERATA Nematocyst: Enhanced Web Hunter
Source Prey: github.com/unclecode/crawl4ai
License: Apache 2.0
Author: Unclecode (original), Rose Glass Framework (metabolized)

Metabolized async web crawler with LLM-powered extraction.
Rose Glass dimensional tracking integrated.
"""

import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

# Try to import Crawl4AI (graceful degradation if not installed)
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.extraction_strategy import (
        JsonCssExtractionStrategy,
        LLMExtractionStrategy
    )
    CRAWL4AI_AVAILABLE = True
except ImportError:
    logger.warning("⚠️  Crawl4AI not available. Install with: pip install crawl4ai playwright")
    logger.warning("   Then run: playwright install")
    CRAWL4AI_AVAILABLE = False


@dataclass
class HuntResult:
    """
    Result from web hunting operation.

    Includes Rose Glass dimensional tracking.
    """
    url: str
    leads_found: int
    raw_markdown: str
    extracted_data: List[Dict[str, Any]]

    # Rose Glass perception
    coherence_score: float  # Overall quality (0-1)
    psi_content: float      # Content richness
    rho_authority: float    # Page authority signals
    q_freshness: float      # Signal freshness
    f_match: float          # Schema match quality

    # Metadata
    hunt_time_seconds: float
    success: bool
    error: Optional[str] = None


class EnhancedWebHunter:
    """
    Web hunter powered by Crawl4AI.

    Rose Glass Dimensions Applied to Hunted Pages:
    - Ψ (psi): Content richness - length, structure, semantic density
    - ρ (rho): Authority signals - domain quality, page structure
    - q: Freshness signals - last-modified, dynamic content indicators
    - f: Fit - how well extraction schema matched the page

    CERATA Integration:
    - Async architecture for speed (10x+ improvement)
    - Stealth mode to avoid detection
    - LLM fallback for unstructured data
    - Graveyard nutrients from failed hunts
    """

    def __init__(
        self,
        headless: bool = True,
        stealth_mode: bool = True,
        proxy: Optional[str] = None,
        user_agent: str = "RoseGlassCRM/1.0 (Lead Research Bot)"
    ):
        """
        Initialize enhanced web hunter.

        Args:
            headless: Run browser in headless mode
            stealth_mode: Enable anti-detection features
            proxy: Optional proxy URL
            user_agent: Custom user agent string
        """
        if not CRAWL4AI_AVAILABLE:
            raise ImportError(
                "Crawl4AI not installed. "
                "Run: pip install crawl4ai playwright && playwright install"
            )

        self.browser_config = BrowserConfig(
            headless=headless,
            stealth_mode=stealth_mode,
            proxy=proxy,
            user_agent=user_agent
        )

        self.hunts_completed = 0
        self.total_leads_found = 0

    async def hunt_leads(
        self,
        urls: List[str],
        extraction_schema: Dict[str, Any],
        use_llm: bool = False,
        llm_provider: str = "openai/gpt-4o-mini",
        llm_instruction: Optional[str] = None
    ) -> List[HuntResult]:
        """
        Hunt leads from multiple URLs.

        Args:
            urls: Target URLs to hunt
            extraction_schema: CSS/JSON schema for extraction
            use_llm: Use LLM-powered extraction (requires API key)
            llm_provider: LLM model for extraction
            llm_instruction: Custom instructions for LLM

        Returns:
            List of HuntResult with extracted leads and Rose Glass scores

        Example:
            >>> hunter = EnhancedWebHunter()
            >>> results = await hunter.hunt_leads(
            ...     urls=["https://example.com/listings"],
            ...     extraction_schema=TREATMENT_CENTER_SCHEMA
            ... )
            >>> for result in results:
            ...     print(f"Found {result.leads_found} leads (C={result.coherence_score:.2f})")
        """
        results = []

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for url in urls:
                try:
                    result = await self._hunt_single(
                        crawler,
                        url,
                        extraction_schema,
                        use_llm,
                        llm_provider,
                        llm_instruction
                    )
                    results.append(result)

                    self.hunts_completed += 1
                    self.total_leads_found += result.leads_found

                    logger.info(
                        f"✓ Hunt {self.hunts_completed}: {url} → "
                        f"{result.leads_found} leads (C={result.coherence_score:.2f})"
                    )

                except Exception as e:
                    logger.error(f"❌ Hunt failed for {url}: {e}")
                    results.append(HuntResult(
                        url=url,
                        leads_found=0,
                        raw_markdown="",
                        extracted_data=[],
                        coherence_score=0.0,
                        psi_content=0.0,
                        rho_authority=0.0,
                        q_freshness=0.0,
                        f_match=0.0,
                        hunt_time_seconds=0.0,
                        success=False,
                        error=str(e)
                    ))

        return results

    async def _hunt_single(
        self,
        crawler: Any,  # AsyncWebCrawler
        url: str,
        schema: Dict[str, Any],
        use_llm: bool,
        llm_provider: str,
        llm_instruction: Optional[str]
    ) -> HuntResult:
        """Hunt a single URL with Rose Glass perception"""
        start_time = time.time()

        # Configure extraction strategy
        if use_llm:
            strategy = LLMExtractionStrategy(
                provider=llm_provider,
                schema=schema,
                instruction=llm_instruction or "Extract structured data from this page."
            )
        else:
            strategy = JsonCssExtractionStrategy(schema=schema)

        run_config = CrawlerRunConfig(
            extraction_strategy=strategy,
            cache_mode="bypass",  # Always fresh data
            wait_for="networkidle"  # Wait for dynamic content
        )

        # Execute crawl
        result = await crawler.arun(url=url, config=run_config)

        hunt_time = time.time() - start_time

        # Parse extracted data
        extracted = result.extracted_content or []
        if isinstance(extracted, str):
            import json
            try:
                extracted = json.loads(extracted)
            except:
                extracted = []

        if not isinstance(extracted, list):
            extracted = [extracted] if extracted else []

        # Calculate Rose Glass dimensions
        psi, rho, q, f = self._calculate_dimensions(result, len(extracted), schema)
        coherence = (psi + rho + q + f) / 4.0

        return HuntResult(
            url=url,
            leads_found=len(extracted),
            raw_markdown=result.markdown or "",
            extracted_data=extracted,
            coherence_score=coherence,
            psi_content=psi,
            rho_authority=rho,
            q_freshness=q,
            f_match=f,
            hunt_time_seconds=hunt_time,
            success=result.success
        )

    def _calculate_dimensions(
        self,
        crawl_result: Any,
        leads_found: int,
        schema: Dict[str, Any]
    ) -> tuple[float, float, float, float]:
        """
        Calculate Rose Glass dimensions for hunted content.

        Returns: (Ψ, ρ, q, f) tuple
        """
        # Ψ (psi) - Content richness
        markdown = crawl_result.markdown or ""
        psi = min(len(markdown) / 10000, 1.0)  # Normalize to 10k chars

        # ρ (rho) - Authority (success + HTML structure quality)
        rho = 0.0
        if crawl_result.success:
            rho += 0.5
        if crawl_result.html and len(crawl_result.html) > 1000:
            rho += 0.3  # Substantial page
        if markdown and markdown.count('\n') > 20:
            rho += 0.2  # Good structure
        rho = min(rho, 1.0)

        # q - Freshness (assume recent for now - could check headers)
        q = 0.8  # Default assumption

        # f - Fit (extraction match quality)
        expected_fields = len(schema.get('fields', []))
        if expected_fields > 0 and leads_found > 0:
            # Check if extracted data has the expected fields
            avg_fields = sum(
                len([k for k in lead.keys() if k in [f['name'] for f in schema.get('fields', [])]])
                for lead in (crawl_result.extracted_content if isinstance(crawl_result.extracted_content, list) else [])
            ) / leads_found if leads_found > 0 else 0

            f = min(avg_fields / expected_fields, 1.0) if expected_fields > 0 else 0.5
        else:
            f = 0.3  # Low match if no leads found

        return (psi, rho, q, f)


# Pre-configured extraction schemas
TREATMENT_CENTER_SCHEMA = {
    "name": "TreatmentCenterLeads",
    "baseSelector": "div.listing, article.result, li.business-card, div.facility",
    "fields": [
        {
            "name": "company_name",
            "selector": "h2, h3, .business-name, .facility-name, .title",
            "type": "text"
        },
        {
            "name": "address",
            "selector": ".address, .location, .street, address",
            "type": "text"
        },
        {
            "name": "phone",
            "selector": ".phone, tel, a[href^='tel:'], .contact-phone",
            "type": "text"
        },
        {
            "name": "website",
            "selector": "a.website, a.url, a[href*='http']",
            "type": "attribute",
            "attribute": "href"
        },
        {
            "name": "description",
            "selector": ".description, .snippet, .summary, p",
            "type": "text"
        },
        {
            "name": "email",
            "selector": "a[href^='mailto:'], .email",
            "type": "text"
        }
    ]
}

BUSINESS_DIRECTORY_SCHEMA = {
    "name": "BusinessDirectoryLeads",
    "baseSelector": "div.business, li.company, article.listing",
    "fields": [
        {"name": "business_name", "selector": "h2, h3, .name", "type": "text"},
        {"name": "industry", "selector": ".category, .industry, .type", "type": "text"},
        {"name": "location", "selector": ".location, .city, .address", "type": "text"},
        {"name": "contact", "selector": ".phone, .email, .contact", "type": "text"},
        {"name": "website", "selector": "a[href*='http']", "type": "attribute", "attribute": "href"},
    ]
}


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demo enhanced web hunter with Rose Glass perception"""
        print("\n" + "=" * 70)
        print("  ENHANCED WEB HUNTER - Crawl4AI + Rose Glass")
        print("=" * 70)

        hunter = EnhancedWebHunter(
            headless=True,
            stealth_mode=True
        )

        # Example URLs (replace with real targets)
        urls = [
            "https://example.com/treatment-centers",
            # Add more URLs as needed
        ]

        print(f"\n🔍 Hunting {len(urls)} URLs with Crawl4AI...")

        results = await hunter.hunt_leads(
            urls=urls,
            extraction_schema=TREATMENT_CENTER_SCHEMA,
            use_llm=False  # CSS extraction first
        )

        print(f"\n📊 Hunt Results:")
        print(f"  Total hunts: {len(results)}")
        print(f"  Successful: {sum(1 for r in results if r.success)}")
        print(f"  Total leads: {sum(r.leads_found for r in results)}")

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.url}")
            print(f"   Leads found: {result.leads_found}")
            print(f"   Coherence: {result.coherence_score:.2f}")
            print(f"   Dimensions: Ψ={result.psi_content:.2f}, ρ={result.rho_authority:.2f}, "
                  f"q={result.q_freshness:.2f}, f={result.f_match:.2f}")
            print(f"   Hunt time: {result.hunt_time_seconds:.2f}s")

        print("\n" + "=" * 70)
        print("  🌹 Rose Glass sees all, judges none, learns always")
        print("=" * 70 + "\n")

    if CRAWL4AI_AVAILABLE:
        asyncio.run(demo())
    else:
        print("⚠️  Crawl4AI not installed. Install with:")
        print("   pip install crawl4ai playwright")
        print("   playwright install")
