"""
Data-based Lead Hunter
======================

Ingests leads from structured data sources (CSV, JSON, CRM exports, manual entry).
Normalizes various formats into LeadData for Rose Glass perception.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import hashlib
import logging
import json
import re

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Import LeadData from core
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.rose_glass_lens import LeadData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FieldMapping:
    """Maps source data fields to LeadData fields"""

    # Identity mappings
    company_name: str = 'company_name'
    contact_name: Optional[str] = None
    contact_title: Optional[str] = None
    contact_email: Optional[str] = None

    # Company signals
    industry: Optional[str] = None
    company_size: Optional[str] = None
    revenue_range: Optional[str] = None

    # Intent signals
    source: str = 'data_import'
    pain_points: Optional[str] = None  # Comma-separated or JSON array
    initial_interest: Optional[str] = None

    # Authority signals
    is_decision_maker: Optional[str] = None
    budget_mentioned: Optional[str] = None
    timeline_mentioned: Optional[str] = None

    # Fit signals
    current_solution: Optional[str] = None
    use_case: Optional[str] = None

    # Engagement signals
    website_visits: Optional[str] = None
    email_opens: Optional[str] = None

    # Notes
    notes: Optional[str] = None


class DataHunter:
    """
    Ingests leads from structured data sources.

    Supports:
    - CSV files (from CRM exports, spreadsheets)
    - JSON files (from APIs, webhooks)
    - Dictionary objects (from manual entry, forms)
    - Pandas DataFrames (for data analysis workflows)
    """

    def __init__(self):
        self.total_ingested = 0
        self.validation_errors = []

    def ingest_csv(
        self,
        filepath: Path,
        field_mapping: Optional[FieldMapping] = None,
        encoding: str = 'utf-8'
    ) -> List[LeadData]:
        """
        Ingest leads from CSV file.

        Args:
            filepath: Path to CSV file
            field_mapping: Custom field mapping (auto-detected if None)
            encoding: File encoding (default utf-8)

        Returns:
            List of LeadData objects
        """
        if not PANDAS_AVAILABLE:
            logger.error("pandas required for CSV ingestion - install with: pip install pandas")
            return []

        logger.info(f"📥 Ingesting CSV: {filepath}")

        try:
            df = pd.read_csv(filepath, encoding=encoding)
            logger.info(f"  Found {len(df)} rows")

            # Auto-detect field mapping if not provided
            if field_mapping is None:
                field_mapping = self._auto_detect_fields(df.columns.tolist())

            leads = self._dataframe_to_leads(df, field_mapping, source=f'csv:{filepath.name}')
            logger.info(f"✓ Ingested {len(leads)} leads from CSV")

            return leads

        except Exception as e:
            logger.error(f"CSV ingestion failed: {e}")
            return []

    def ingest_json(
        self,
        filepath: Path,
        field_mapping: Optional[FieldMapping] = None
    ) -> List[LeadData]:
        """
        Ingest leads from JSON file.

        Supports both single object and array of objects.
        """
        logger.info(f"📥 Ingesting JSON: {filepath}")

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Handle single object vs array
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                logger.error("JSON must be object or array of objects")
                return []

            logger.info(f"  Found {len(data)} records")

            # Auto-detect field mapping if not provided
            if field_mapping is None and data:
                field_mapping = self._auto_detect_fields(data[0].keys())

            leads = []
            for record in data:
                lead = self._dict_to_lead(record, field_mapping, source=f'json:{filepath.name}')
                if lead:
                    leads.append(lead)

            logger.info(f"✓ Ingested {len(leads)} leads from JSON")
            return leads

        except Exception as e:
            logger.error(f"JSON ingestion failed: {e}")
            return []

    def ingest_dict(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        field_mapping: Optional[FieldMapping] = None,
        source: str = 'manual_entry'
    ) -> List[LeadData]:
        """
        Ingest leads from dictionary or list of dictionaries.

        Useful for:
        - Web form submissions
        - API webhooks
        - Manual lead entry
        """
        # Handle single dict vs list
        if isinstance(data, dict):
            data = [data]

        if field_mapping is None and data:
            field_mapping = self._auto_detect_fields(data[0].keys())

        leads = []
        for record in data:
            lead = self._dict_to_lead(record, field_mapping, source=source)
            if lead:
                leads.append(lead)

        logger.info(f"✓ Ingested {len(leads)} leads from dict")
        return leads

    def ingest_dataframe(
        self,
        df: Any,  # pandas.DataFrame
        field_mapping: Optional[FieldMapping] = None,
        source: str = 'dataframe'
    ) -> List[LeadData]:
        """Ingest from pandas DataFrame (for data analysis workflows)"""
        if not PANDAS_AVAILABLE:
            logger.error("pandas required")
            return []

        if field_mapping is None:
            field_mapping = self._auto_detect_fields(df.columns.tolist())

        return self._dataframe_to_leads(df, field_mapping, source)

    def create_manual_lead(
        self,
        company_name: str,
        contact_name: Optional[str] = None,
        contact_title: Optional[str] = None,
        contact_email: Optional[str] = None,
        industry: Optional[str] = None,
        company_size: Optional[str] = None,
        pain_points: Optional[List[str]] = None,
        notes: str = '',
        **kwargs
    ) -> LeadData:
        """
        Manually create a single lead.

        Quick entry for discovered leads (networking, events, referrals).
        """
        lead_id = hashlib.md5(
            f"{company_name}_{contact_email or contact_name or datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        return LeadData(
            lead_id=lead_id,
            company_name=company_name,
            contact_name=contact_name,
            contact_title=contact_title,
            contact_email=contact_email,
            industry=industry,
            company_size=company_size,
            pain_points=pain_points or [],
            source='manual',
            notes=notes,
            **kwargs
        )

    def _auto_detect_fields(self, columns: List[str]) -> FieldMapping:
        """
        Auto-detect field mappings from column names.

        Handles common CRM export formats (Salesforce, HubSpot, Pipedrive).
        """
        mapping = FieldMapping()

        # Normalize column names
        col_map = {col.lower().replace(' ', '_'): col for col in columns}

        # Company name detection
        company_variants = ['company_name', 'company', 'organization', 'account', 'account_name']
        for variant in company_variants:
            if variant in col_map:
                mapping.company_name = col_map[variant]
                break

        # Contact name
        name_variants = ['contact_name', 'name', 'full_name', 'contact', 'first_name']
        for variant in name_variants:
            if variant in col_map:
                mapping.contact_name = col_map[variant]
                break

        # Contact title
        title_variants = ['title', 'contact_title', 'job_title', 'position', 'role']
        for variant in title_variants:
            if variant in col_map:
                mapping.contact_title = col_map[variant]
                break

        # Email
        email_variants = ['email', 'contact_email', 'email_address', 'work_email']
        for variant in email_variants:
            if variant in col_map:
                mapping.contact_email = col_map[variant]
                break

        # Industry
        industry_variants = ['industry', 'sector', 'vertical', 'market']
        for variant in industry_variants:
            if variant in col_map:
                mapping.industry = col_map[variant]
                break

        # Company size
        size_variants = ['company_size', 'size', 'employees', 'employee_count']
        for variant in size_variants:
            if variant in col_map:
                mapping.company_size = col_map[variant]
                break

        # Pain points
        pain_variants = ['pain_points', 'challenges', 'problems', 'needs', 'requirements']
        for variant in pain_variants:
            if variant in col_map:
                mapping.pain_points = col_map[variant]
                break

        # Notes
        notes_variants = ['notes', 'description', 'comments', 'details']
        for variant in notes_variants:
            if variant in col_map:
                mapping.notes = col_map[variant]
                break

        logger.info(f"  Auto-detected mappings: company={mapping.company_name}, email={mapping.contact_email}")
        return mapping

    def _dataframe_to_leads(
        self,
        df: Any,
        field_mapping: FieldMapping,
        source: str
    ) -> List[LeadData]:
        """Convert DataFrame to list of LeadData"""
        leads = []

        for idx, row in df.iterrows():
            try:
                lead = self._dict_to_lead(row.to_dict(), field_mapping, source)
                if lead:
                    leads.append(lead)
            except Exception as e:
                logger.warning(f"  Row {idx} failed: {e}")
                self.validation_errors.append({
                    'row': idx,
                    'error': str(e),
                    'data': row.to_dict()
                })

        return leads

    def _dict_to_lead(
        self,
        data: Dict[str, Any],
        field_mapping: FieldMapping,
        source: str
    ) -> Optional[LeadData]:
        """Convert dictionary to LeadData using field mapping"""

        # Required field
        company_name = data.get(field_mapping.company_name)
        if not company_name or pd.isna(company_name):
            logger.warning(f"  Skipping record - missing company name")
            return None

        # Generate lead ID
        lead_id = hashlib.md5(
            f"{company_name}_{data.get(field_mapping.contact_email or 'email', '')}_{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Extract optional fields
        def get_field(mapping_field: Optional[str], default=None):
            if mapping_field and mapping_field in data:
                value = data[mapping_field]
                return value if not (PANDAS_AVAILABLE and pd.isna(value)) else default
            return default

        contact_name = get_field(field_mapping.contact_name)
        contact_title = get_field(field_mapping.contact_title)
        contact_email = get_field(field_mapping.contact_email)

        industry = get_field(field_mapping.industry)
        company_size = self._normalize_company_size(get_field(field_mapping.company_size))

        # Parse pain points (could be string, list, or JSON)
        pain_points = self._parse_list_field(get_field(field_mapping.pain_points))

        # Boolean fields
        is_decision_maker = self._parse_bool(get_field(field_mapping.is_decision_maker))
        budget_mentioned = self._parse_bool(get_field(field_mapping.budget_mentioned))

        # Numeric fields
        website_visits = self._parse_int(get_field(field_mapping.website_visits), 0)
        email_opens = self._parse_int(get_field(field_mapping.email_opens), 0)

        # Text fields
        notes = get_field(field_mapping.notes, '')
        initial_interest = get_field(field_mapping.initial_interest)
        use_case = get_field(field_mapping.use_case)
        current_solution = get_field(field_mapping.current_solution)
        timeline_mentioned = get_field(field_mapping.timeline_mentioned)

        return LeadData(
            lead_id=lead_id,
            company_name=str(company_name),
            contact_name=contact_name,
            contact_title=contact_title,
            contact_email=contact_email,
            industry=industry,
            company_size=company_size,
            pain_points=pain_points,
            source=source,
            initial_interest=initial_interest,
            is_decision_maker=is_decision_maker,
            budget_mentioned=budget_mentioned,
            timeline_mentioned=timeline_mentioned,
            current_solution=current_solution,
            use_case=use_case,
            website_visits=website_visits,
            email_opens=email_opens,
            notes=notes,
        )

    def _normalize_company_size(self, size: Optional[str]) -> Optional[str]:
        """Normalize company size to standard categories"""
        if not size:
            return None

        size_lower = str(size).lower()

        # Map various formats to standard categories
        if any(x in size_lower for x in ['1-10', '1-20', 'startup', 'seed']):
            return 'startup'
        elif any(x in size_lower for x in ['11-50', '21-50', '51-100', 'small', 'smb']):
            return 'smb'
        elif any(x in size_lower for x in ['101-500', '201-500', 'mid-market', 'medium']):
            return 'mid-market'
        elif any(x in size_lower for x in ['500+', '1000+', 'enterprise', 'large']):
            return 'enterprise'

        return size  # Return as-is if no match

    def _parse_list_field(self, value: Any) -> List[str]:
        """Parse a field that could be a list, comma-separated string, or JSON array"""
        if not value:
            return []

        if isinstance(value, list):
            return [str(x) for x in value]

        if isinstance(value, str):
            # Try JSON
            if value.startswith('['):
                try:
                    return json.loads(value)
                except:
                    pass

            # Try comma-separated
            if ',' in value:
                return [x.strip() for x in value.split(',')]

            # Single value
            return [value] if value else []

        return []

    def _parse_bool(self, value: Any) -> Optional[bool]:
        """Parse boolean from various formats"""
        if value is None or (PANDAS_AVAILABLE and pd.isna(value)):
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ['true', 'yes', 'y', '1']:
                return True
            elif value_lower in ['false', 'no', 'n', '0']:
                return False

        return None

    def _parse_int(self, value: Any, default: int = 0) -> int:
        """Parse integer from various formats"""
        if value is None or (PANDAS_AVAILABLE and pd.isna(value)):
            return default

        try:
            return int(value)
        except (ValueError, TypeError):
            return default


# Example usage
if __name__ == "__main__":
    hunter = DataHunter()

    # Example 1: Manual lead creation
    print("\n📝 Manual Lead Entry:")
    lead = hunter.create_manual_lead(
        company_name="Acme Corp",
        contact_name="John Smith",
        contact_title="VP of Engineering",
        contact_email="john@acme.com",
        industry="SaaS",
        company_size="mid-market",
        pain_points=["security compliance", "access control"],
        notes="Met at TechConf 2026 - very interested in demo"
    )
    print(f"  Created lead: {lead.lead_id} - {lead.company_name}")
    print(f"  Pain points: {lead.pain_points}")

    # Example 2: Dictionary ingestion
    print("\n📥 Dictionary Ingestion:")
    data = [
        {
            'company_name': 'Beta Inc',
            'contact_name': 'Jane Doe',
            'email': 'jane@beta.com',
            'title': 'CTO',
            'industry': 'Fintech',
            'pain_points': 'data encryption, compliance',
        },
        {
            'company_name': 'Gamma LLC',
            'contact_name': 'Bob Wilson',
            'email': 'bob@gamma.com',
            'title': 'Director IT',
            'industry': 'Healthcare',
            'pain_points': 'HIPAA compliance, user management',
        }
    ]

    leads = hunter.ingest_dict(data, source='web_form')
    print(f"  Ingested {len(leads)} leads")
    for lead in leads:
        print(f"    - {lead.company_name} ({lead.industry}): {len(lead.pain_points)} pain points")

    # Example 3: CSV ingestion (demo)
    print("\n📁 CSV Ingestion (demo):")
    print("  Usage: hunter.ingest_csv(Path('leads.csv'))")
    print("  Auto-detects field mappings for common CRM exports")
    print("  Supports: Salesforce, HubSpot, Pipedrive, custom CSVs")
