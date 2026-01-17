"""
CERATA AI Scraper
Metabolized from kaymen99/ai-web-scraper pattern
Source Prey: github.com/kaymen99/ai-web-scraper
License: MIT (compatible)

LLM-powered lead extraction with Rose Glass perception.
Combines Crawl4AI async crawling with intelligent data parsing.
"""

import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
import csv
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import dependencies (graceful degradation)
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    logger.warning("Pydantic not available - install with: pip install pydantic")
    PYDANTIC_AVAILABLE = False

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    logger.warning("Crawl4AI not available - install with: pip install crawl4ai playwright")
    CRAWL4AI_AVAILABLE = False


if PYDANTIC_AVAILABLE:
    class BusinessLead(BaseModel):
        """Pydantic model for extracted business lead"""
        business_name: str = Field(..., description="Full company/facility name")
        address: Optional[str] = Field(None, description="Street address, city, state, ZIP")
        phone: Optional[str] = Field(None, description="Primary phone number")
        website: Optional[str] = Field(None, description="Website URL")
        email: Optional[str] = Field(None, description="Email address")
        description: Optional[str] = Field(None, description="Brief description of services")

        # Rose Glass intent signals (detected by LLM)
        has_hiring_signal: bool = Field(False, description="Mentions hiring, jobs, careers")
        has_expansion_signal: bool = Field(False, description="Mentions growth, new locations, expanding")
        has_tech_signal: bool = Field(False, description="Mentions technology, software, digital")
        has_pain_signal: bool = Field(False, description="Expresses problems or challenges")

        # Metadata
        source_url: Optional[str] = Field(None, description="URL where lead was found")
        extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat())

        class Config:
            json_schema_extra = {
                "example": {
                    "business_name": "Acme Recovery Center",
                    "address": "123 Main St, Draper, UT 84020",
                    "phone": "(801) 555-1234",
                    "website": "https://acmerecovery.com",
                    "email": "info@acmerecovery.com",
                    "description": "30-day residential treatment program",
                    "has_hiring_signal": True,
                    "has_expansion_signal": False,
                    "has_tech_signal": False,
                    "has_pain_signal": False
                }
            }
else:
    # Fallback if Pydantic not available
    class BusinessLead:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)


class AIScraper:
    """
    AI-powered web scraper using LLM extraction.

    Combines Crawl4AI async crawling with LLM intelligence for:
    - Unstructured data extraction
    - Intent signal detection
    - Automated schema generation
    - Rose Glass dimensional perception

    CERATA Philosophy:
    - Perceive, don't prescribe: LLM detects patterns we specify
    - Learn from failures: Track extraction misses in graveyard
    - Evolve through trials: Compare LLM vs CSS extraction
    """

    DEFAULT_INSTRUCTIONS = """
    Extract business contact information from this page.

    For each business/facility listing found, extract:
    - business_name: Full company or facility name
    - address: Complete street address including city, state, ZIP
    - phone: Primary contact phone number
    - website: Website URL if visible
    - email: Email address if available
    - description: Brief 1-2 sentence description of what they do

    Also detect these Rose Glass intent signals:
    - has_hiring_signal: True if mentions "hiring", "careers", "jobs", "join our team"
    - has_expansion_signal: True if mentions "growth", "new location", "expanding", "opening soon"
    - has_tech_signal: True if mentions "technology", "software", "digital", "tech stack"
    - has_pain_signal: True if expresses problems like "struggling", "need", "looking for", "help with"

    Return as a JSON array of objects matching the schema.
    If no businesses found, return empty array [].
    """

    def __init__(
        self,
        llm_provider: str = "openai/gpt-4o-mini",
        max_pages: int = 5,
        headless: bool = True,
        instruction: Optional[str] = None
    ):
        """
        Initialize AI scraper.

        Args:
            llm_provider: LLM model (e.g., "openai/gpt-4o-mini", "anthropic/claude-3-haiku")
            max_pages: Maximum pages to scrape per hunt
            headless: Run browser in headless mode
            instruction: Custom LLM instructions (uses DEFAULT if None)
        """
        if not CRAWL4AI_AVAILABLE:
            raise ImportError("Crawl4AI required - install with: pip install crawl4ai playwright")

        if not PYDANTIC_AVAILABLE:
            logger.warning("Pydantic not available - validation limited")

        self.llm_provider = llm_provider
        self.max_pages = max_pages
        self.instruction = instruction or self.DEFAULT_INSTRUCTIONS

        self.browser_config = BrowserConfig(
            headless=headless,
            stealth_mode=True
        )

        self.leads_scraped = 0
        self.pages_processed = 0

    async def scrape_leads(
        self,
        base_url: str,
        page_param: str = "page",
        start_page: int = 1
    ) -> List[BusinessLead]:
        """
        Scrape leads from paginated URL using LLM extraction.

        Args:
            base_url: Target URL (e.g., "https://example.com/directory?state=utah")
            page_param: Query parameter for pagination (default "page")
            start_page: Starting page number (default 1)

        Returns:
            List of BusinessLead objects with Rose Glass signals

        Example:
            >>> scraper = AIScraper()
            >>> leads = await scraper.scrape_leads(
            ...     base_url="https://example.com/treatment-centers?state=utah"
            ... )
            >>> print(f"Found {len(leads)} leads")
            >>> for lead in leads:
            ...     if lead.has_pain_signal:
            ...         print(f"Pain signal: {lead.business_name}")
        """
        all_leads = []

        # Create LLM extraction strategy
        strategy = LLMExtractionStrategy(
            provider=self.llm_provider,
            instruction=self.instruction
        )

        run_config = CrawlerRunConfig(
            extraction_strategy=strategy,
            cache_mode="bypass"
        )

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for page_num in range(start_page, start_page + self.max_pages):
                # Build paginated URL
                separator = "&" if "?" in base_url else "?"
                url = f"{base_url}{separator}{page_param}={page_num}"

                try:
                    logger.info(f"🔍 Scraping page {page_num}: {url}")

                    result = await crawler.arun(url=url, config=run_config)

                    if result.extracted_content:
                        # Parse LLM response
                        data = self._parse_llm_response(result.extracted_content)

                        if data:
                            for item in data:
                                if PYDANTIC_AVAILABLE:
                                    try:
                                        lead = BusinessLead(**item, source_url=url)
                                        all_leads.append(lead)
                                    except Exception as e:
                                        logger.warning(f"Invalid lead data: {e}")
                                else:
                                    # Fallback without Pydantic validation
                                    item['source_url'] = url
                                    all_leads.append(BusinessLead(**item))

                            self.pages_processed += 1
                            self.leads_scraped += len(data)

                            logger.info(f"  ✓ Found {len(data)} leads on page {page_num}")
                        else:
                            logger.info(f"  ⚠️  No leads found on page {page_num} - stopping")
                            break  # No more results, stop pagination

                except Exception as e:
                    logger.error(f"  ❌ Page {page_num} failed: {e}")
                    break  # Stop on error

        logger.info(f"✓ Scraping complete: {len(all_leads)} total leads from {self.pages_processed} pages")
        return all_leads

    def _parse_llm_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse LLM-extracted content to list of dicts"""
        try:
            # Try direct JSON parsing
            data = json.loads(content)

            # Ensure it's a list
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                logger.warning(f"Unexpected LLM response type: {type(data)}")
                return []

            return data

        except json.JSONDecodeError:
            # LLM might have returned markdown-wrapped JSON
            import re
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass

            logger.error("Failed to parse LLM response as JSON")
            return []

    def export_to_csv(
        self,
        leads: List[BusinessLead],
        filepath: Path
    ):
        """
        Export leads to CSV file.

        Args:
            leads: List of BusinessLead objects
            filepath: Output CSV path
        """
        if not leads:
            logger.warning("No leads to export")
            return

        # Get field names
        if PYDANTIC_AVAILABLE:
            fieldnames = list(BusinessLead.model_fields.keys())
        else:
            # Get fields from first lead
            fieldnames = list(vars(leads[0]).keys())

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for lead in leads:
                if PYDANTIC_AVAILABLE:
                    writer.writerow(lead.model_dump())
                else:
                    writer.writerow(vars(lead))

        logger.info(f"✓ Exported {len(leads)} leads to {filepath}")

    def export_to_json(
        self,
        leads: List[BusinessLead],
        filepath: Path
    ):
        """
        Export leads to JSON file.

        Args:
            leads: List of BusinessLead objects
            filepath: Output JSON path
        """
        if not leads:
            logger.warning("No leads to export")
            return

        data = []
        for lead in leads:
            if PYDANTIC_AVAILABLE:
                data.append(lead.model_dump())
            else:
                data.append(vars(lead))

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"✓ Exported {len(leads)} leads to {filepath}")

    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            "total_leads_scraped": self.leads_scraped,
            "pages_processed": self.pages_processed,
            "avg_leads_per_page": self.leads_scraped / self.pages_processed if self.pages_processed > 0 else 0,
            "llm_provider": self.llm_provider,
        }


# Example usage
if __name__ == "__main__":
    async def demo():
        """Demo AI scraper with Rose Glass intent detection"""
        print("\n" + "=" * 70)
        print("  AI SCRAPER - LLM-Powered Lead Extraction")
        print("=" * 70)

        scraper = AIScraper(
            llm_provider="openai/gpt-4o-mini",
            max_pages=2  # Demo: only 2 pages
        )

        # Example URL (replace with actual target)
        base_url = "https://example.com/treatment-centers?state=utah"

        print(f"\n🔍 Scraping: {base_url}")
        print("   Using LLM for intelligent extraction...")

        leads = await scraper.scrape_leads(base_url)

        print(f"\n📊 Results:")
        print(f"  Total leads: {len(leads)}")

        # Show Rose Glass signals
        hiring = sum(1 for l in leads if l.has_hiring_signal)
        expansion = sum(1 for l in leads if l.has_expansion_signal)
        tech = sum(1 for l in leads if l.has_tech_signal)
        pain = sum(1 for l in leads if l.has_pain_signal)

        print(f"\n  Rose Glass Signals Detected:")
        print(f"    Hiring signals: {hiring}")
        print(f"    Expansion signals: {expansion}")
        print(f"    Tech signals: {tech}")
        print(f"    Pain signals: {pain}")

        if leads:
            print(f"\n  Sample Lead:")
            lead = leads[0]
            print(f"    Name: {lead.business_name}")
            print(f"    Phone: {lead.phone}")
            print(f"    Website: {lead.website}")

            # Export
            output_dir = Path("data/scraped_leads")
            output_dir.mkdir(parents=True, exist_ok=True)

            scraper.export_to_csv(leads, output_dir / "leads.csv")
            scraper.export_to_json(leads, output_dir / "leads.json")

        stats = scraper.get_stats()
        print(f"\n  Stats:")
        for key, value in stats.items():
            print(f"    {key}: {value}")

        print("\n" + "=" * 70)
        print("  🌹 Rose Glass sees all, judges none, learns always")
        print("=" * 70 + "\n")

    if CRAWL4AI_AVAILABLE and PYDANTIC_AVAILABLE:
        asyncio.run(demo())
    else:
        print("⚠️  Dependencies not installed:")
        if not CRAWL4AI_AVAILABLE:
            print("   pip install crawl4ai playwright")
            print("   playwright install")
        if not PYDANTIC_AVAILABLE:
            print("   pip install pydantic")
