"""Hunter engines for lead discovery"""
from .web_hunter import WebHunter, HuntCriteria
from .data_hunter import DataHunter

__all__ = ['WebHunter', 'HuntCriteria', 'DataHunter']
