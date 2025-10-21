"""
SWOT Analysis Tool - Generates comprehensive SWOT analysis for companies
"""
import yfinance as yf
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class SWOTTool:
    """Tool to generate SWOT analysis for companies"""

    name = "generate_swot_analysis"
    description = """
    Generates a comprehensive SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis
    for a given company using financial data and market intelligence.

    The analysis considers:
    - Financial performance metrics
    - Market position and competitive advantages
    - Industry trends and market conditions
    - Risk factors and external threats

    Example usage:
    - generate_swot_analysis(ticker="AAPL")
    - generate_swot_analysis(ticker="TSLA")
    """

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Optional LLM client for generating analysis
        """
        self.llm_client = llm_client

    def _gather_company_data(self, ticker: str) -> Dict[str, Any]:
        """Gather comprehensive company data for SWOT analysis"""
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            # Get recent news for qualitative insights
            news = ticker_obj.news[:5] if hasattr(ticker_obj, 'news') else []

            return {
                "basic_info": {
                    "name": info.get("longName", "N/A"),
                    "sector": info.get("sector", "N/A"),
                    "industry": info.get("industry", "N/A"),
                    "description": info.get("longBusinessSummary", "N/A")[:500],
                },
                "financial_health": {
                    "market_cap": info.get("marketCap", "N/A"),
                    "revenue": info.get("totalRevenue", "N/A"),
                    "revenue_growth": info.get("revenueGrowth", "N/A"),
                    "profit_margin": info.get("profitMargins", "N/A"),
                    "operating_margin": info.get("operatingMargins", "N/A"),
                    "roe": info.get("returnOnEquity", "N/A"),
                    "debt_to_equity": info.get("debtToEquity", "N/A"),
                    "current_ratio": info.get("currentRatio", "N/A"),
                },
                "market_position": {
                    "beta": info.get("beta", "N/A"),
                    "52_week_change": info.get("52WeekChange", "N/A"),
                    "analyst_recommendation": info.get("recommendationKey", "N/A"),
                    "target_price": info.get("targetMeanPrice", "N/A"),
                    "current_price": info.get("currentPrice", "N/A"),
                },
                "valuation": {
                    "pe_ratio": info.get("trailingPE", "N/A"),
                    "forward_pe": info.get("forwardPE", "N/A"),
                    "peg_ratio": info.get("pegRatio", "N/A"),
                    "price_to_book": info.get("priceToBook", "N/A"),
                },
                "recent_news": [
                    {
                        "title": item.get("title", ""),
                        "publisher": item.get("publisher", "")
                    }
                    for item in news
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def _generate_swot_from_data(self, company_data: Dict[str, Any]) -> Dict[str, list]:
        """Generate SWOT analysis based on company data"""

        swot = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }

        basic = company_data.get("basic_info", {})
        financial = company_data.get("financial_health", {})
        market = company_data.get("market_position", {})
        valuation = company_data.get("valuation", {})

        # Analyze STRENGTHS
        if isinstance(financial.get("profit_margin"), (int, float)) and financial["profit_margin"] > 0.15:
            swot["strengths"].append(f"Strong profit margin of {financial['profit_margin']:.1%}")

        if isinstance(financial.get("roe"), (int, float)) and financial["roe"] > 0.15:
            swot["strengths"].append(f"Excellent return on equity of {financial['roe']:.1%}")

        if isinstance(financial.get("current_ratio"), (int, float)) and financial["current_ratio"] > 1.5:
            swot["strengths"].append(f"Healthy liquidity with current ratio of {financial['current_ratio']:.2f}")

        if isinstance(financial.get("revenue_growth"), (int, float)) and financial["revenue_growth"] > 0.1:
            swot["strengths"].append(f"Strong revenue growth of {financial['revenue_growth']:.1%}")

        if market.get("analyst_recommendation") in ["buy", "strong buy"]:
            swot["strengths"].append(f"Positive analyst sentiment: {market['analyst_recommendation']}")

        # Analyze WEAKNESSES
        if isinstance(financial.get("debt_to_equity"), (int, float)) and financial["debt_to_equity"] > 2.0:
            swot["weaknesses"].append(f"High debt-to-equity ratio of {financial['debt_to_equity']:.2f}")

        if isinstance(financial.get("current_ratio"), (int, float)) and financial["current_ratio"] < 1.0:
            swot["weaknesses"].append(f"Low liquidity with current ratio of {financial['current_ratio']:.2f}")

        if isinstance(valuation.get("pe_ratio"), (int, float)) and valuation["pe_ratio"] > 30:
            swot["weaknesses"].append(f"High P/E ratio of {valuation['pe_ratio']:.2f} may indicate overvaluation")

        if isinstance(financial.get("operating_margin"), (int, float)) and financial["operating_margin"] < 0.05:
            swot["weaknesses"].append(f"Low operating margin of {financial['operating_margin']:.1%}")

        # Analyze OPPORTUNITIES
        if isinstance(financial.get("revenue_growth"), (int, float)) and financial["revenue_growth"] > 0:
            swot["opportunities"].append("Continue expanding in growing markets")

        if isinstance(valuation.get("peg_ratio"), (int, float)) and valuation["peg_ratio"] < 1.0:
            swot["opportunities"].append("Potential undervaluation based on growth prospects")

        current_price = market.get("current_price", 0)
        target_price = market.get("target_price", 0)
        if isinstance(current_price, (int, float)) and isinstance(target_price, (int, float)):
            if current_price > 0 and target_price > current_price * 1.1:
                upside = ((target_price - current_price) / current_price) * 100
                swot["opportunities"].append(f"Analyst target price suggests {upside:.1f}% upside potential")

        swot["opportunities"].append(f"Leverage position in {basic.get('industry', 'the industry')} sector")

        # Analyze THREATS
        if isinstance(market.get("beta"), (int, float)) and market["beta"] > 1.5:
            swot["threats"].append(f"High market volatility (beta: {market['beta']:.2f})")

        if isinstance(financial.get("debt_to_equity"), (int, float)) and financial["debt_to_equity"] > 1.5:
            swot["threats"].append("Elevated debt levels may limit financial flexibility")

        if market.get("analyst_recommendation") in ["sell", "strong sell", "underperform"]:
            swot["threats"].append(f"Negative analyst sentiment: {market['analyst_recommendation']}")

        swot["threats"].append(f"Competition and disruption in {basic.get('industry', 'the industry')}")
        swot["threats"].append("Macroeconomic uncertainties and market volatility")

        # Add generic items if categories are empty
        if not swot["strengths"]:
            swot["strengths"].append("Established market presence")
        if not swot["weaknesses"]:
            swot["weaknesses"].append("Limited data available for detailed assessment")
        if not swot["opportunities"]:
            swot["opportunities"].append("Market expansion and innovation")
        if not swot["threats"]:
            swot["threats"].append("Industry competition and market dynamics")

        return swot

    def _format_swot_report(self, ticker: str, company_data: Dict, swot: Dict) -> str:
        """Format SWOT analysis into readable report"""

        basic = company_data.get("basic_info", {})

        report = f"SWOT Analysis for {basic.get('name', ticker.upper())} ({ticker.upper()})\n"
        report += "=" * 70 + "\n\n"

        report += f"Sector: {basic.get('sector', 'N/A')}\n"
        report += f"Industry: {basic.get('industry', 'N/A')}\n\n"

        report += "=" * 70 + "\n\n"

        # Strengths
        report += "STRENGTHS\n"
        report += "-" * 70 + "\n"
        for i, item in enumerate(swot.get("strengths", []), 1):
            report += f"{i}. {item}\n"
        report += "\n"

        # Weaknesses
        report += "WEAKNESSES\n"
        report += "-" * 70 + "\n"
        for i, item in enumerate(swot.get("weaknesses", []), 1):
            report += f"{i}. {item}\n"
        report += "\n"

        # Opportunities
        report += "OPPORTUNITIES\n"
        report += "-" * 70 + "\n"
        for i, item in enumerate(swot.get("opportunities", []), 1):
            report += f"{i}. {item}\n"
        report += "\n"

        # Threats
        report += "THREATS\n"
        report += "-" * 70 + "\n"
        for i, item in enumerate(swot.get("threats", []), 1):
            report += f"{i}. {item}\n"
        report += "\n"

        report += "=" * 70 + "\n"
        report += "Note: This SWOT analysis is generated from publicly available financial data\n"
        report += "and should be used as a starting point for further research and analysis.\n"

        return report

    def __call__(self, ticker: str) -> str:
        """
        Generate SWOT analysis for a company

        Args:
            ticker: Stock ticker symbol

        Returns:
            Formatted SWOT analysis report
        """
        try:
            ticker = ticker.upper()

            # Gather company data
            company_data = self._gather_company_data(ticker)

            if "error" in company_data:
                return f"Error generating SWOT analysis for {ticker}: {company_data['error']}"

            # Generate SWOT
            swot = self._generate_swot_from_data(company_data)

            # Format report
            report = self._format_swot_report(ticker, company_data, swot)

            return report

        except Exception as e:
            return f"Error generating SWOT analysis for {ticker}: {str(e)}"


def get_swot_tool(llm_client=None):
    """Factory function to create the SWOT analysis tool"""
    return SWOTTool(llm_client=llm_client)
