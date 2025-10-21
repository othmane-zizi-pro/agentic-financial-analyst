"""
Financial Metrics Tool - Fetches real-time and historical financial data for companies
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class FinancialMetricsInput(BaseModel):
    """Input schema for financial metrics tool"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)")
    metrics_type: str = Field(
        default="summary",
        description="Type of metrics: 'summary', 'detailed', 'ratios', or 'historical'"
    )


class FinancialMetricsTool:
    """Tool to fetch financial metrics for a company"""

    name = "get_financial_metrics"
    description = """
    Fetches comprehensive financial metrics for a given company ticker.

    Available metrics types:
    - summary: Key financial highlights (market cap, P/E, revenue, etc.)
    - detailed: Full financial statements (income, balance sheet, cash flow)
    - ratios: Financial ratios (profitability, liquidity, efficiency)
    - historical: Historical price and volume data

    Example usage:
    - get_financial_metrics(ticker="AAPL", metrics_type="summary")
    - get_financial_metrics(ticker="MSFT", metrics_type="ratios")
    """

    def __init__(self):
        self.cache = {}

    def _get_summary_metrics(self, ticker_obj) -> Dict[str, Any]:
        """Get summary financial metrics"""
        info = ticker_obj.info

        return {
            "company_name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "current_price": info.get("currentPrice", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "price_to_book": info.get("priceToBook", "N/A"),
            "revenue": info.get("totalRevenue", "N/A"),
            "revenue_growth": info.get("revenueGrowth", "N/A"),
            "profit_margin": info.get("profitMargins", "N/A"),
            "operating_margin": info.get("operatingMargins", "N/A"),
            "roe": info.get("returnOnEquity", "N/A"),
            "roa": info.get("returnOnAssets", "N/A"),
            "debt_to_equity": info.get("debtToEquity", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "analyst_recommendation": info.get("recommendationKey", "N/A"),
        }

    def _get_financial_ratios(self, ticker_obj) -> Dict[str, Any]:
        """Calculate and return key financial ratios"""
        info = ticker_obj.info

        return {
            "profitability_ratios": {
                "gross_margin": info.get("grossMargins", "N/A"),
                "operating_margin": info.get("operatingMargins", "N/A"),
                "profit_margin": info.get("profitMargins", "N/A"),
                "roe": info.get("returnOnEquity", "N/A"),
                "roa": info.get("returnOnAssets", "N/A"),
            },
            "liquidity_ratios": {
                "current_ratio": info.get("currentRatio", "N/A"),
                "quick_ratio": info.get("quickRatio", "N/A"),
            },
            "leverage_ratios": {
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "debt_to_assets": info.get("debtToAssets", "N/A"),
            },
            "valuation_ratios": {
                "pe_ratio": info.get("trailingPE", "N/A"),
                "forward_pe": info.get("forwardPE", "N/A"),
                "peg_ratio": info.get("pegRatio", "N/A"),
                "price_to_book": info.get("priceToBook", "N/A"),
                "price_to_sales": info.get("priceToSalesTrailing12Months", "N/A"),
                "ev_to_revenue": info.get("enterpriseToRevenue", "N/A"),
                "ev_to_ebitda": info.get("enterpriseToEbitda", "N/A"),
            },
            "efficiency_ratios": {
                "asset_turnover": info.get("assetTurnover", "N/A"),
                "inventory_turnover": info.get("inventoryTurnover", "N/A"),
            }
        }

    def _get_historical_data(self, ticker_obj, period: str = "1y") -> Dict[str, Any]:
        """Get historical price data"""
        hist = ticker_obj.history(period=period)

        if hist.empty:
            return {"error": "No historical data available"}

        return {
            "period": period,
            "data_points": len(hist),
            "latest_close": float(hist['Close'].iloc[-1]),
            "period_high": float(hist['High'].max()),
            "period_low": float(hist['Low'].min()),
            "average_volume": float(hist['Volume'].mean()),
            "price_change_percent": float(
                ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            ),
        }

    def __call__(self, ticker: str, metrics_type: str = "summary") -> str:
        """
        Fetch financial metrics for a company

        Args:
            ticker: Stock ticker symbol
            metrics_type: Type of metrics to fetch

        Returns:
            Formatted string with financial metrics
        """
        try:
            # Fetch company data
            ticker_obj = yf.Ticker(ticker.upper())

            if metrics_type == "summary":
                metrics = self._get_summary_metrics(ticker_obj)
            elif metrics_type == "ratios":
                metrics = self._get_financial_ratios(ticker_obj)
            elif metrics_type == "historical":
                metrics = self._get_historical_data(ticker_obj)
            elif metrics_type == "detailed":
                # Get all available data
                metrics = {
                    "summary": self._get_summary_metrics(ticker_obj),
                    "ratios": self._get_financial_ratios(ticker_obj),
                    "historical_1y": self._get_historical_data(ticker_obj, "1y"),
                }
            else:
                return f"Error: Unknown metrics_type '{metrics_type}'"

            # Format output
            output = f"Financial Metrics for {ticker.upper()} ({metrics_type}):\n\n"
            output += self._format_dict(metrics)

            return output

        except Exception as e:
            return f"Error fetching financial metrics for {ticker}: {str(e)}"

    def _format_dict(self, data: Dict, indent: int = 0) -> str:
        """Recursively format dictionary for readable output"""
        output = ""
        for key, value in data.items():
            if isinstance(value, dict):
                output += f"{'  ' * indent}{key}:\n"
                output += self._format_dict(value, indent + 1)
            else:
                # Format numbers
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if abs(value) > 1_000_000_000:
                        value = f"${value / 1_000_000_000:.2f}B"
                    elif abs(value) > 1_000_000:
                        value = f"${value / 1_000_000:.2f}M"
                    elif abs(value) > 1000:
                        value = f"{value:,.2f}"
                    else:
                        value = f"{value:.4f}"

                output += f"{'  ' * indent}{key.replace('_', ' ').title()}: {value}\n"

        return output


def get_financial_metrics_tool():
    """Factory function to create the tool"""
    return FinancialMetricsTool()
