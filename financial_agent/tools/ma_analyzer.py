"""
M&A Analysis Tool - Analyzes merger and acquisition activity among industry peers
"""
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta


class MATool:
    """Tool to analyze M&A activity for companies and their peers"""

    name = "analyze_ma_activity"
    description = """
    Analyzes merger and acquisition (M&A) activity for a company and its industry peers.

    This tool:
    1. Identifies peer companies in the same sector/industry
    2. Searches for recent M&A announcements and news
    3. Analyzes M&A trends and strategic implications
    4. Provides competitive intelligence on industry consolidation

    Example usage:
    - analyze_ma_activity(ticker="MSFT")
    - analyze_ma_activity(ticker="JPM")
    """

    def __init__(self, llm_client=None):
        """
        Args:
            llm_client: Optional LLM client for analyzing unstructured data
        """
        self.llm_client = llm_client

    def _get_peer_companies(self, ticker: str) -> List[Dict[str, str]]:
        """Identify peer companies in the same sector/industry"""
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            sector = info.get("sector", "")
            industry = info.get("industry", "")

            # This is a simplified approach - in production, you'd use a more
            # comprehensive database or API for peer identification
            # For now, we'll return info about the company and note peers should be added

            return [{
                "ticker": ticker.upper(),
                "name": info.get("longName", "N/A"),
                "sector": sector,
                "industry": industry,
                "market_cap": info.get("marketCap", "N/A")
            }]

        except Exception as e:
            return [{"error": f"Could not fetch peer data: {str(e)}"}]

    def _search_ma_news(self, company_name: str, ticker: str) -> List[Dict[str, Any]]:
        """
        Search for M&A news and announcements

        Note: This is a placeholder implementation. In production, you would:
        1. Use news APIs (e.g., NewsAPI, AlphaVantage News, Bloomberg API)
        2. Scrape financial news websites
        3. Access SEC EDGAR filings for 8-K forms
        4. Use specialized M&A databases
        """
        news_items = []

        try:
            # Get recent news from yfinance
            ticker_obj = yf.Ticker(ticker.upper())
            news = ticker_obj.news

            # Filter for M&A related news
            ma_keywords = [
                'merger', 'acquisition', 'acquire', 'bought', 'purchase',
                'takeover', 'deal', 'buyout', 'consolidation', 'm&a'
            ]

            for item in news[:10]:  # Limit to recent news
                title = item.get('title', '').lower()
                summary = item.get('summary', '').lower()

                # Check if news is M&A related
                if any(keyword in title or keyword in summary for keyword in ma_keywords):
                    news_items.append({
                        'title': item.get('title', 'N/A'),
                        'publisher': item.get('publisher', 'N/A'),
                        'link': item.get('link', 'N/A'),
                        'published': datetime.fromtimestamp(
                            item.get('providerPublishTime', 0)
                        ).strftime('%Y-%m-%d'),
                        'summary': item.get('summary', 'N/A')[:300]  # Truncate
                    })

            return news_items

        except Exception as e:
            return [{"error": f"Could not fetch M&A news: {str(e)}"}]

    def _analyze_ma_trends(
        self,
        company_info: Dict,
        peer_info: List[Dict],
        news_items: List[Dict]
    ) -> str:
        """Analyze M&A trends using LLM if available, otherwise provide structured summary"""

        # Prepare context for analysis
        context = f"""
Company: {company_info.get('name', 'N/A')} ({company_info.get('ticker', 'N/A')})
Sector: {company_info.get('sector', 'N/A')}
Industry: {company_info.get('industry', 'N/A')}

Recent M&A-Related News ({len(news_items)} items):
"""

        for i, news in enumerate(news_items[:5], 1):
            context += f"\n{i}. {news.get('title', 'N/A')}"
            context += f"\n   Date: {news.get('published', 'N/A')}"
            context += f"\n   Summary: {news.get('summary', 'N/A')[:200]}...\n"

        if self.llm_client:
            # Use LLM for deep analysis
            prompt = f"""
{context}

Based on the above information, provide a comprehensive M&A analysis including:

1. **Recent M&A Activity Summary**: What M&A activities has this company been involved in?

2. **Strategic Rationale**: What appears to be the strategic rationale behind these moves?

3. **Industry Consolidation Trends**: What does this tell us about consolidation in this industry?

4. **Competitive Implications**: How might these M&A activities affect the competitive landscape?

5. **Future Outlook**: What M&A activity might we expect going forward?

Provide a concise, structured analysis.
"""
            try:
                # This would call the actual LLM - implementation depends on your LLM setup
                # For now, return the prompt as a placeholder
                return f"[LLM Analysis would go here]\n\n{context}"
            except Exception as e:
                return f"LLM analysis failed: {str(e)}\n\n{context}"
        else:
            # Return structured summary without LLM
            return context

    def __call__(self, ticker: str) -> str:
        """
        Analyze M&A activity for a company

        Args:
            ticker: Stock ticker symbol

        Returns:
            Formatted M&A analysis report
        """
        try:
            ticker = ticker.upper()

            # Get company and peer information
            peers = self._get_peer_companies(ticker)

            if not peers or 'error' in peers[0]:
                return f"Error: Could not analyze M&A activity for {ticker}"

            company_info = peers[0]
            company_name = company_info.get('name', ticker)

            # Search for M&A news
            ma_news = self._search_ma_news(company_name, ticker)

            # Build report
            report = f"M&A Activity Analysis for {company_name} ({ticker})\n"
            report += "=" * 60 + "\n\n"

            report += f"Company Information:\n"
            report += f"  Sector: {company_info.get('sector', 'N/A')}\n"
            report += f"  Industry: {company_info.get('industry', 'N/A')}\n"
            report += f"  Market Cap: {company_info.get('market_cap', 'N/A')}\n\n"

            if ma_news and 'error' not in ma_news[0]:
                report += f"Recent M&A-Related News ({len(ma_news)} items found):\n\n"
                for i, news in enumerate(ma_news, 1):
                    report += f"{i}. {news.get('title', 'N/A')}\n"
                    report += f"   Published: {news.get('published', 'N/A')}\n"
                    report += f"   Source: {news.get('publisher', 'N/A')}\n"
                    report += f"   Summary: {news.get('summary', 'N/A')}\n"
                    report += f"   Link: {news.get('link', 'N/A')}\n\n"

                # Add trend analysis
                report += "\n" + "=" * 60 + "\n"
                report += "M&A TREND ANALYSIS\n"
                report += "=" * 60 + "\n\n"
                report += self._analyze_ma_trends(company_info, peers, ma_news)

            else:
                report += "No recent M&A-related news found for this company.\n"
                report += "\nThis could indicate:\n"
                report += "  - The company is not actively pursuing M&A\n"
                report += "  - M&A activities are confidential/pre-announcement\n"
                report += "  - The industry is experiencing low M&A activity\n"

            return report

        except Exception as e:
            return f"Error analyzing M&A activity for {ticker}: {str(e)}"


def get_ma_tool(llm_client=None):
    """Factory function to create the M&A analysis tool"""
    return MATool(llm_client=llm_client)
