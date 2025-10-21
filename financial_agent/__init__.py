"""
Financial Analyst Agent for Databricks
An AI-powered financial analysis tool built with Mosaic AI Agent Framework
"""

__version__ = "1.0.0"
__author__ = "Databricks Hackathon Team"

from .agent import create_financial_agent, FinancialAnalystAgent
from .tools import (
    get_financial_metrics_tool,
    get_ma_tool,
    get_swot_tool
)

__all__ = [
    'create_financial_agent',
    'FinancialAnalystAgent',
    'get_financial_metrics_tool',
    'get_ma_tool',
    'get_swot_tool',
]
