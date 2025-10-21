"""
Financial Analyst App - Clean Version
NO yfinance dependency - uses direct Yahoo Finance API
Enhanced with LLM analysis (with fallback to rules-based)
"""
import gradio as gr
import requests
from typing import Dict, Any
from datetime import datetime
import json
import os

# ============================================================================
# HARDCODED FALLBACK DATA (for when API fails)
# ============================================================================

FALLBACK_DATA = {
    'AAPL': {
        'price': {'longName': 'Apple Inc.', 'regularMarketPrice': 178.72, 'marketCap': 2800000000000},
        'assetProfile': {'sector': 'Technology', 'industry': 'Consumer Electronics'},
        'summaryDetail': {'fiftyTwoWeekHigh': 199.62, 'fiftyTwoWeekLow': 164.08, 'trailingPE': 29.5, 'forwardPE': 27.8, 'beta': 1.24},
        'financialData': {'profitMargins': 0.25, 'operatingMargins': 0.30, 'returnOnEquity': 1.47, 'returnOnAssets': 0.22, 'revenueGrowth': 0.06, 'currentRatio': 0.98, 'debtToEquity': 1.96, 'quickRatio': 0.85, 'recommendationKey': 'buy'},
        'defaultKeyStatistics': {'priceToBook': 45.2, 'pegRatio': 2.8}
    },
    'MSFT': {
        'price': {'longName': 'Microsoft Corporation', 'regularMarketPrice': 378.91, 'marketCap': 2820000000000},
        'assetProfile': {'sector': 'Technology', 'industry': 'Software—Infrastructure'},
        'summaryDetail': {'fiftyTwoWeekHigh': 468.35, 'fiftyTwoWeekLow': 362.90, 'trailingPE': 35.2, 'forwardPE': 31.5, 'beta': 0.89},
        'financialData': {'profitMargins': 0.36, 'operatingMargins': 0.42, 'returnOnEquity': 0.42, 'returnOnAssets': 0.18, 'revenueGrowth': 0.13, 'currentRatio': 1.25, 'debtToEquity': 0.48, 'quickRatio': 1.22, 'recommendationKey': 'buy'},
        'defaultKeyStatistics': {'priceToBook': 12.5, 'pegRatio': 2.1}
    },
    'GOOGL': {
        'price': {'longName': 'Alphabet Inc.', 'regularMarketPrice': 139.58, 'marketCap': 1750000000000},
        'assetProfile': {'sector': 'Technology', 'industry': 'Internet Content & Information'},
        'summaryDetail': {'fiftyTwoWeekHigh': 153.78, 'fiftyTwoWeekLow': 121.46, 'trailingPE': 24.8, 'forwardPE': 21.3, 'beta': 1.06},
        'financialData': {'profitMargins': 0.26, 'operatingMargins': 0.29, 'returnOnEquity': 0.28, 'returnOnAssets': 0.16, 'revenueGrowth': 0.11, 'currentRatio': 2.28, 'debtToEquity': 0.11, 'quickRatio': 2.24, 'recommendationKey': 'buy'},
        'defaultKeyStatistics': {'priceToBook': 6.2, 'pegRatio': 1.9}
    },
    'TSLA': {
        'price': {'longName': 'Tesla, Inc.', 'regularMarketPrice': 248.50, 'marketCap': 790000000000},
        'assetProfile': {'sector': 'Consumer Cyclical', 'industry': 'Auto Manufacturers'},
        'summaryDetail': {'fiftyTwoWeekHigh': 299.29, 'fiftyTwoWeekLow': 138.80, 'trailingPE': 65.4, 'forwardPE': 58.2, 'beta': 2.31},
        'financialData': {'profitMargins': 0.15, 'operatingMargins': 0.11, 'returnOnEquity': 0.28, 'returnOnAssets': 0.09, 'revenueGrowth': 0.19, 'currentRatio': 1.73, 'debtToEquity': 0.17, 'quickRatio': 1.22, 'recommendationKey': 'hold'},
        'defaultKeyStatistics': {'priceToBook': 12.8, 'pegRatio': 3.5}
    },
    'NVDA': {
        'price': {'longName': 'NVIDIA Corporation', 'regularMarketPrice': 128.45, 'marketCap': 3160000000000},
        'assetProfile': {'sector': 'Technology', 'industry': 'Semiconductors'},
        'summaryDetail': {'fiftyTwoWeekHigh': 140.76, 'fiftyTwoWeekLow': 39.23, 'trailingPE': 68.2, 'forwardPE': 35.8, 'beta': 1.68},
        'financialData': {'profitMargins': 0.55, 'operatingMargins': 0.62, 'returnOnEquity': 1.23, 'returnOnAssets': 0.53, 'revenueGrowth': 1.22, 'currentRatio': 3.42, 'debtToEquity': 0.32, 'quickRatio': 2.98, 'recommendationKey': 'buy'},
        'defaultKeyStatistics': {'priceToBook': 55.3, 'pegRatio': 0.9}
    }
}

FALLBACK_NEWS = {
    'AAPL': [
        {'title': 'Apple Announces New iPhone 16 with AI Features', 'publisher': 'TechCrunch', 'providerPublishTime': 1729500000, 'link': 'https://example.com/apple-news'},
        {'title': 'Apple Stock Hits New High on Strong Services Revenue', 'publisher': 'CNBC', 'providerPublishTime': 1729400000, 'link': 'https://example.com/apple-stock'}
    ],
    'MSFT': [
        {'title': 'Microsoft Expands Azure AI Services', 'publisher': 'Reuters', 'providerPublishTime': 1729500000, 'link': 'https://example.com/msft-news'},
        {'title': 'Microsoft Cloud Revenue Exceeds Expectations', 'publisher': 'Bloomberg', 'providerPublishTime': 1729400000, 'link': 'https://example.com/msft-cloud'}
    ],
    'GOOGL': [
        {'title': 'Google Launches New AI Search Features', 'publisher': 'The Verge', 'providerPublishTime': 1729500000, 'link': 'https://example.com/googl-news'},
        {'title': 'Alphabet Reports Strong Ad Revenue Growth', 'publisher': 'WSJ', 'providerPublishTime': 1729400000, 'link': 'https://example.com/googl-earnings'}
    ],
    'TSLA': [
        {'title': 'Tesla Cybertruck Production Ramps Up', 'publisher': 'Electrek', 'providerPublishTime': 1729500000, 'link': 'https://example.com/tesla-news'},
        {'title': 'Tesla Stock Rises on Strong Delivery Numbers', 'publisher': 'MarketWatch', 'providerPublishTime': 1729400000, 'link': 'https://example.com/tesla-stock'}
    ],
    'NVDA': [
        {'title': 'NVIDIA Unveils Next-Gen AI Chips', 'publisher': 'AnandTech', 'providerPublishTime': 1729500000, 'link': 'https://example.com/nvda-news'},
        {'title': 'NVIDIA Continues to Dominate AI Chip Market', 'publisher': 'Forbes', 'providerPublishTime': 1729400000, 'link': 'https://example.com/nvda-market'}
    ]
}

# ============================================================================
# LLM ENHANCEMENT LAYER (with fallback)
# ============================================================================

def enhance_with_llm(user_query: str, raw_data: str, analysis_type: str) -> tuple[str, str]:
    """
    Enhance analysis with LLM insights
    Returns: (enhanced_result, model_used)
    """
    try:
        # Try Databricks Foundation Model API
        host = os.getenv('DATABRICKS_HOST')
        token = os.getenv('DATABRICKS_CLIENT_SECRET') or os.getenv('DATABRICKS_TOKEN')

        if not host or not token:
            raise Exception("Databricks credentials not available")

        # Use OpenAI-compatible endpoint for Databricks models
        from openai import OpenAI

        client = OpenAI(
            api_key=token,
            base_url=f"https://{host}/serving-endpoints"
        )

        # Try DBRX first, then Llama as fallback
        models_to_try = [
            "databricks-dbrx-instruct",
            "databricks-meta-llama-3-1-70b-instruct",
            "databricks-meta-llama-3-70b-instruct"
        ]

        prompt = f"""You are a professional financial analyst.

User Question: {user_query}

Analysis Type: {analysis_type}

Raw Data:
{raw_data}

Provide a concise, actionable analysis with:
1. 📊 Key Insights (2-3 most important points)
2. ⚠️ Risks to Watch
3. 💡 Recommendation (with brief reasoning)

Keep it under 200 words and actionable."""

        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a concise financial analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )

                llm_analysis = response.choices[0].message.content
                model_name = model.replace('databricks-', '').upper()

                enhanced = f"""{raw_data}

{'='*70}

🤖 AI-Enhanced Analysis (Model: {model_name})
{'='*70}

{llm_analysis}

{'='*70}
💡 Powered by {model_name} on Databricks
"""
                return enhanced, model_name

            except Exception as model_error:
                print(f"Failed to use {model}: {model_error}")
                continue

        # If all models fail
        raise Exception("All LLM models failed")

    except Exception as e:
        print(f"LLM enhancement failed: {e}, using rules-based output")
        # Fallback: just return raw data
        return f"""{raw_data}

{'='*70}
ℹ️  Analysis Mode: Rules-Based (LLM unavailable)
{'='*70}""", "RULES-BASED"


# ============================================================================
# YAHOO FINANCE API WRAPPER (NO YFINANCE DEPENDENCY)
# ============================================================================

def get_stock_data(ticker: str) -> Dict:
    """Fetch stock data directly from Yahoo Finance API with fallback"""
    ticker = ticker.upper()

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Get quote data
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {
            'modules': 'price,summaryDetail,financialData,defaultKeyStatistics,assetProfile'
        }

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        result = data.get('quoteSummary', {}).get('result', [])
        if not result:
            raise Exception("No data returned from API")

        print(f"✓ Successfully fetched live data for {ticker}")
        return result[0]
    except Exception as e:
        print(f"API failed for {ticker}: {e}, using fallback data")
        # Use fallback data if available
        if ticker in FALLBACK_DATA:
            print(f"✓ Using fallback data for {ticker}")
            return FALLBACK_DATA[ticker]
        return {}


def get_stock_news(ticker: str) -> list:
    """Fetch stock news from Yahoo Finance with fallback"""
    ticker = ticker.upper()

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        url = f"https://query2.finance.yahoo.com/v1/finance/search"
        params = {'q': ticker, 'quotesCount': 1, 'newsCount': 10}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        news = data.get('news', [])
        if news:
            print(f"✓ Successfully fetched live news for {ticker}")
            return news
        raise Exception("No news returned from API")
    except Exception as e:
        print(f"News API failed for {ticker}: {e}, using fallback news")
        # Use fallback news if available
        if ticker in FALLBACK_NEWS:
            print(f"✓ Using fallback news for {ticker}")
            return FALLBACK_NEWS[ticker]
        return []


# ============================================================================
# STANDALONE TOOLS
# ============================================================================

class FinancialMetricsTool:
    """Standalone financial metrics tool"""

    def __call__(self, ticker: str, metrics_type: str = "summary") -> str:
        try:
            data = get_stock_data(ticker.upper())
            if not data:
                return f"""Error: Could not fetch data for {ticker}.

Supported companies with fallback data:
- Apple (AAPL)
- Microsoft (MSFT)
- Google/Alphabet (GOOGL)
- Tesla (TSLA)
- NVIDIA (NVDA)

Please try one of these companies or verify the ticker symbol."""

            if metrics_type == "summary":
                return self._get_summary(data, ticker.upper())
            elif metrics_type == "ratios":
                return self._get_ratios(data, ticker.upper())
            else:
                return self._get_summary(data, ticker.upper())

        except Exception as e:
            return f"Error fetching data for {ticker}: {str(e)}"

    def _get_value(self, data: Dict, *keys, default='N/A'):
        """Safely extract nested values"""
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, {})
            else:
                return default

        if isinstance(data, dict):
            return data.get('raw', data.get('fmt', default))
        return data if data is not None else default

    def _get_summary(self, data: Dict, ticker: str) -> str:
        output = f"Financial Metrics for {ticker}\n"
        output += "=" * 70 + "\n\n"

        # Company info
        profile = data.get('assetProfile', {})
        price = data.get('price', {})
        summary = data.get('summaryDetail', {})
        financial = data.get('financialData', {})
        stats = data.get('defaultKeyStatistics', {})

        output += f"Company: {self._get_value(price, 'longName')}\n"
        output += f"Sector: {self._get_value(profile, 'sector')}\n"
        output += f"Industry: {self._get_value(profile, 'industry')}\n\n"

        # Market data
        market_cap = self._get_value(price, 'marketCap', default=0)
        if isinstance(market_cap, (int, float)) and market_cap > 1_000_000_000:
            market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
        elif isinstance(market_cap, (int, float)) and market_cap > 0:
            market_cap_str = f"${market_cap / 1_000_000:.2f}M"
        else:
            market_cap_str = "N/A"

        output += f"Market Cap: {market_cap_str}\n"
        output += f"Current Price: ${self._get_value(price, 'regularMarketPrice')}\n"
        output += f"52 Week High: ${self._get_value(summary, 'fiftyTwoWeekHigh')}\n"
        output += f"52 Week Low: ${self._get_value(summary, 'fiftyTwoWeekLow')}\n\n"

        # Valuation
        output += "Valuation Metrics:\n"
        output += f"  P/E Ratio: {self._get_value(summary, 'trailingPE')}\n"
        output += f"  Forward P/E: {self._get_value(summary, 'forwardPE')}\n"
        output += f"  Price to Book: {self._get_value(stats, 'priceToBook')}\n"
        output += f"  PEG Ratio: {self._get_value(stats, 'pegRatio')}\n\n"

        # Profitability
        output += "Profitability:\n"
        profit_margin = self._get_value(financial, 'profitMargins', default=0)
        operating_margin = self._get_value(financial, 'operatingMargins', default=0)

        if isinstance(profit_margin, (int, float)) and profit_margin > 0:
            output += f"  Profit Margin: {profit_margin * 100:.2f}%\n"
        else:
            output += "  Profit Margin: N/A\n"

        if isinstance(operating_margin, (int, float)) and operating_margin > 0:
            output += f"  Operating Margin: {operating_margin * 100:.2f}%\n"
        else:
            output += "  Operating Margin: N/A\n"

        output += f"  ROE: {self._get_value(financial, 'returnOnEquity')}\n"
        output += f"  ROA: {self._get_value(financial, 'returnOnAssets')}\n\n"

        # Growth
        revenue_growth = self._get_value(financial, 'revenueGrowth', default=0)
        output += "Growth:\n"
        if isinstance(revenue_growth, (int, float)) and revenue_growth != 0:
            output += f"  Revenue Growth: {revenue_growth * 100:.2f}%\n"
        else:
            output += "  Revenue Growth: N/A\n"
        output += f"  Earnings Growth: {self._get_value(financial, 'earningsGrowth')}\n\n"

        # Financial Health
        output += "Financial Health:\n"
        output += f"  Current Ratio: {self._get_value(financial, 'currentRatio')}\n"
        output += f"  Debt to Equity: {self._get_value(financial, 'debtToEquity')}\n"
        output += f"  Quick Ratio: {self._get_value(financial, 'quickRatio')}\n\n"

        # Analyst Opinion
        rec = self._get_value(financial, 'recommendationKey', default='N/A')
        output += f"Analyst Recommendation: {rec.upper() if isinstance(rec, str) else rec}\n"

        return output

    def _get_ratios(self, data: Dict, ticker: str) -> str:
        output = f"Financial Ratios for {ticker}\n"
        output += "=" * 70 + "\n\n"

        financial = data.get('financialData', {})
        summary = data.get('summaryDetail', {})
        stats = data.get('defaultKeyStatistics', {})

        output += "Profitability Ratios:\n"
        output += f"  Gross Margin: {self._get_value(financial, 'grossMargins')}\n"
        output += f"  Operating Margin: {self._get_value(financial, 'operatingMargins')}\n"
        output += f"  Profit Margin: {self._get_value(financial, 'profitMargins')}\n"
        output += f"  ROE: {self._get_value(financial, 'returnOnEquity')}\n"
        output += f"  ROA: {self._get_value(financial, 'returnOnAssets')}\n\n"

        output += "Valuation Ratios:\n"
        output += f"  P/E Ratio: {self._get_value(summary, 'trailingPE')}\n"
        output += f"  Forward P/E: {self._get_value(summary, 'forwardPE')}\n"
        output += f"  PEG Ratio: {self._get_value(stats, 'pegRatio')}\n"
        output += f"  Price to Book: {self._get_value(stats, 'priceToBook')}\n"
        output += f"  Price to Sales: {self._get_value(summary, 'priceToSalesTrailing12Months')}\n\n"

        output += "Liquidity Ratios:\n"
        output += f"  Current Ratio: {self._get_value(financial, 'currentRatio')}\n"
        output += f"  Quick Ratio: {self._get_value(financial, 'quickRatio')}\n\n"

        output += "Leverage Ratios:\n"
        output += f"  Debt to Equity: {self._get_value(financial, 'debtToEquity')}\n"

        return output


class MATool:
    """Standalone M&A analysis tool"""

    def __call__(self, ticker: str) -> str:
        try:
            data = get_stock_data(ticker.upper())
            news = get_stock_news(ticker.upper())

            if not data:
                return f"Error: Could not fetch data for {ticker}. Please verify the ticker symbol."

            output = f"M&A Activity Analysis for {ticker.upper()}\n"
            output += "=" * 70 + "\n\n"

            price = data.get('price', {})
            profile = data.get('assetProfile', {})

            output += f"Company: {self._get_value(price, 'longName')}\n"
            output += f"Sector: {self._get_value(profile, 'sector')}\n"
            output += f"Industry: {self._get_value(profile, 'industry')}\n\n"

            # Filter for M&A related news
            ma_keywords = ['merger', 'acquisition', 'acquire', 'bought', 'purchase',
                          'takeover', 'deal', 'buyout', 'm&a']

            ma_news = []
            for item in news[:15]:
                title = item.get('title', '').lower()
                if any(keyword in title for keyword in ma_keywords):
                    ma_news.append(item)

            if ma_news:
                output += f"Recent M&A-Related News ({len(ma_news)} items):\n\n"
                for i, item in enumerate(ma_news[:5], 1):
                    output += f"{i}. {item.get('title', 'N/A')}\n"
                    output += f"   Publisher: {item.get('publisher', 'N/A')}\n"
                    pub_time = item.get('providerPublishTime', 0)
                    if pub_time:
                        date_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d')
                        output += f"   Date: {date_str}\n"
                    output += f"   Link: {item.get('link', 'N/A')}\n\n"
            else:
                output += "No recent M&A-related news found.\n"
                output += "This could indicate the company is not actively pursuing M&A.\n"

            return output

        except Exception as e:
            return f"Error analyzing M&A for {ticker}: {str(e)}"

    def _get_value(self, data: Dict, key: str, default='N/A'):
        """Safely extract values"""
        val = data.get(key, default)
        if isinstance(val, dict):
            return val.get('raw', val.get('fmt', default))
        return val if val is not None else default


class SWOTTool:
    """Standalone SWOT analysis tool"""

    def __call__(self, ticker: str) -> str:
        try:
            data = get_stock_data(ticker.upper())

            if not data:
                return f"Error: Could not fetch data for {ticker}. Please verify the ticker symbol."

            output = f"SWOT Analysis for {ticker.upper()}\n"
            output += "=" * 70 + "\n\n"

            price = data.get('price', {})
            profile = data.get('assetProfile', {})
            financial = data.get('financialData', {})
            summary = data.get('summaryDetail', {})

            output += f"Company: {self._get_value(price, 'longName')}\n"
            output += f"Sector: {self._get_value(profile, 'sector')}\n"
            output += f"Industry: {self._get_value(profile, 'industry')}\n\n"

            output += "=" * 70 + "\n\n"

            # STRENGTHS
            output += "STRENGTHS\n"
            output += "-" * 70 + "\n"

            strengths = []
            profit_margin = self._get_value(financial, 'profitMargins', default=0)
            roe = self._get_value(financial, 'returnOnEquity', default=0)
            current_ratio = self._get_value(financial, 'currentRatio', default=0)
            revenue_growth = self._get_value(financial, 'revenueGrowth', default=0)

            if isinstance(profit_margin, (int, float)) and profit_margin > 0.15:
                strengths.append(f"Strong profit margin of {profit_margin * 100:.1f}%")
            if isinstance(roe, (int, float)) and roe > 0.15:
                strengths.append(f"Excellent ROE of {roe * 100:.1f}%")
            if isinstance(current_ratio, (int, float)) and current_ratio > 1.5:
                strengths.append(f"Healthy liquidity with current ratio of {current_ratio:.2f}")
            if isinstance(revenue_growth, (int, float)) and revenue_growth > 0.1:
                strengths.append(f"Strong revenue growth of {revenue_growth * 100:.1f}%")

            if not strengths:
                strengths.append("Established market presence")

            for i, s in enumerate(strengths, 1):
                output += f"{i}. {s}\n"

            # WEAKNESSES
            output += "\nWEAKNESSES\n"
            output += "-" * 70 + "\n"

            weaknesses = []
            debt_equity = self._get_value(financial, 'debtToEquity', default=0)
            pe_ratio = self._get_value(summary, 'trailingPE', default=0)

            if isinstance(debt_equity, (int, float)) and debt_equity > 2.0:
                weaknesses.append(f"High debt-to-equity ratio of {debt_equity:.2f}")
            if isinstance(current_ratio, (int, float)) and 0 < current_ratio < 1.0:
                weaknesses.append(f"Low liquidity with current ratio of {current_ratio:.2f}")
            if isinstance(pe_ratio, (int, float)) and pe_ratio > 30:
                weaknesses.append(f"High P/E ratio of {pe_ratio:.2f} may indicate overvaluation")

            if not weaknesses:
                weaknesses.append("Limited public data available")

            for i, w in enumerate(weaknesses, 1):
                output += f"{i}. {w}\n"

            # OPPORTUNITIES
            output += "\nOPPORTUNITIES\n"
            output += "-" * 70 + "\n"

            opportunities = []
            if isinstance(revenue_growth, (int, float)) and revenue_growth > 0:
                opportunities.append("Continue expanding in growing markets")

            peg_ratio = self._get_value(financial, 'pegRatio', default=0)
            if isinstance(peg_ratio, (int, float)) and 0 < peg_ratio < 1.0:
                opportunities.append("Potential undervaluation based on growth")

            industry = self._get_value(profile, 'industry', default='the industry')
            opportunities.append(f"Leverage position in {industry}")

            for i, o in enumerate(opportunities, 1):
                output += f"{i}. {o}\n"

            # THREATS
            output += "\nTHREATS\n"
            output += "-" * 70 + "\n"

            threats = []
            beta = self._get_value(summary, 'beta', default=0)

            if isinstance(beta, (int, float)) and beta > 1.5:
                threats.append(f"High market volatility (beta: {beta:.2f})")
            if isinstance(debt_equity, (int, float)) and debt_equity > 1.5:
                threats.append("Elevated debt levels")

            threats.append(f"Competition in {industry}")
            threats.append("Market volatility")

            for i, t in enumerate(threats, 1):
                output += f"{i}. {t}\n"

            output += "\n" + "=" * 70 + "\n"

            return output

        except Exception as e:
            return f"Error generating SWOT for {ticker}: {str(e)}"

    def _get_value(self, data: Dict, key: str, default='N/A'):
        """Safely extract values"""
        val = data.get(key, default)
        if isinstance(val, dict):
            return val.get('raw', val.get('fmt', default))
        return val if val is not None else default


# ============================================================================
# GRADIO UI
# ============================================================================

# Initialize tools
financial_tool = FinancialMetricsTool()
ma_tool = MATool()
swot_tool = SWOTTool()

# Popular company tickers
POPULAR_TICKERS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "TSLA", "AMZN"],
    "Finance": ["JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "DHR", "CVS"],
    "Consumer": ["WMT", "HD", "NKE", "MCD", "SBUX", "COST", "TGT", "LOW"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO"],
    "Industrial": ["CAT", "BA", "GE", "HON", "UPS", "LMT", "DE", "MMM"]
}


def analyze_company(ticker, analysis_type):
    """Main analysis function"""
    if not ticker:
        return "Please enter a stock ticker (e.g., AAPL, MSFT)"

    ticker = ticker.upper()

    if analysis_type == "Financial Metrics":
        return financial_tool(ticker=ticker, metrics_type="summary")
    elif analysis_type == "M&A Analysis":
        return ma_tool(ticker=ticker)
    elif analysis_type == "SWOT Analysis":
        return swot_tool(ticker=ticker)
    else:
        return "Please select an analysis type"


def update_companies(sector):
    """Update company dropdown based on sector"""
    if sector:
        return gr.update(choices=POPULAR_TICKERS[sector], value=None)
    return gr.update(choices=[], value=None)


def smart_agent(user_message):
    """
    AGENTIC ROUTING: Analyzes user message and calls appropriate tool
    """
    message_lower = user_message.lower()

    # Company name to ticker mapping
    COMPANY_TO_TICKER = {
        'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 'alphabet': 'GOOGL',
        'meta': 'META', 'facebook': 'META', 'amazon': 'AMZN', 'tesla': 'TSLA',
        'nvidia': 'NVDA', 'amd': 'AMD', 'intel': 'INTC', 'netflix': 'NFLX',
        'disney': 'DIS', 'nike': 'NKE', 'walmart': 'WMT', 'target': 'TGT',
        'jpmorgan': 'JPM', 'chase': 'JPM', 'goldman': 'GS', 'morgan': 'MS',
        'visa': 'V', 'mastercard': 'MA', 'paypal': 'PYPL', 'square': 'SQ',
        'boeing': 'BA', 'airbus': 'AIR', 'lockheed': 'LMT', 'raytheon': 'RTX',
        'pfizer': 'PFE', 'moderna': 'MRNA', 'johnson': 'JNJ', 'abbvie': 'ABBV',
        'exxon': 'XOM', 'chevron': 'CVX', 'shell': 'SHEL', 'bp': 'BP',
        'starbucks': 'SBUX', 'mcdonalds': 'MCD', 'chipotle': 'CMG',
        'ford': 'F', 'gm': 'GM', 'general motors': 'GM', 'toyota': 'TM'
    }

    # Extract ticker from message
    words = user_message.upper().split()
    potential_tickers = [w.strip('.,!?') for w in words if 2 <= len(w) <= 5 and w.isalpha()]

    # Check if any word is a company name
    ticker = None
    for word in user_message.lower().split():
        word_clean = word.strip('.,!?')
        if word_clean in COMPANY_TO_TICKER:
            ticker = COMPANY_TO_TICKER[word_clean]
            break

    # If no company name found, use extracted ticker
    if not ticker:
        if not potential_tickers:
            return """I need a company ticker or name to analyze!

Try asking:
- "Analyze AAPL" or "Analyze Apple"
- "What are the financial metrics for Tesla?"
- "Give me a SWOT for NVDA" or "SWOT for Nvidia"
- "M&A activity for Microsoft"

Available: AAPL, MSFT, GOOGL, TSLA, NVDA, AMZN, META, etc."""

        ticker = potential_tickers[0]

    # AGENTIC DECISION: Choose tool based on keywords
    header = f"🤖 **Agent Decision:** Analyzing {ticker}...\n\n"

    # Determine analysis type and get raw data
    if any(word in message_lower for word in ['swot', 'strengths', 'weaknesses', 'opportunities', 'threats', 'strategic']):
        analysis_type = "SWOT Analysis"
        header += f"**Tool Selected:** {analysis_type}\n\n"
        header += "=" * 70 + "\n"
        raw_data = swot_tool(ticker=ticker)

    # Check for M&A keywords
    elif any(word in message_lower for word in ['m&a', 'merger', 'acquisition', 'deal', 'buyout', 'acquire']):
        analysis_type = "M&A Analysis"
        header += f"**Tool Selected:** {analysis_type}\n\n"
        header += "=" * 70 + "\n"
        raw_data = ma_tool(ticker=ticker)

    # Check for ratios/detailed metrics
    elif any(word in message_lower for word in ['ratio', 'ratios', 'valuation', 'profitability', 'leverage']):
        analysis_type = "Financial Ratios"
        header += f"**Tool Selected:** {analysis_type}\n\n"
        header += "=" * 70 + "\n"
        raw_data = financial_tool(ticker=ticker, metrics_type="ratios")

    # Default to financial metrics
    else:
        analysis_type = "Financial Metrics"
        header += f"**Tool Selected:** {analysis_type}\n\n"
        header += "=" * 70 + "\n"
        raw_data = financial_tool(ticker=ticker, metrics_type="summary")

    # Enhance with LLM (with fallback to rules-based)
    enhanced_data, model_used = enhance_with_llm(user_message, raw_data, analysis_type)

    return header + enhanced_data


# Create Gradio interface
with gr.Blocks(title="Financial Analyst Agent", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    # 📊 Financial Analyst Agent with AI Enhancement 🤖
    ### Powered by Databricks Foundation Models

    Get real-time financial analysis enhanced with AI insights.
    **Features:** Smart routing • LLM-powered analysis • Fallback guarantee
    """)

    with gr.Tabs():
        # Tab 1: Smart Agent Chat
        with gr.Tab("🤖 Smart Agent Chat"):
            gr.Markdown("""
            ### Ask Questions in Natural Language
            The agent will automatically decide which tool to use!

            **Try these examples:**
            - "Analyze Apple" or "Analyze AAPL"
            - "What are the strengths and weaknesses of Tesla?"
            - "Show me M&A activity for Microsoft"
            - "What are the financial ratios for Nvidia?"

            **Supported companies (with guaranteed fallback data):**
            Apple (AAPL) | Microsoft (MSFT) | Google (GOOGL) | Tesla (TSLA) | NVIDIA (NVDA)

            *You can use either company names or ticker symbols!*
            """)

            chat_input = gr.Textbox(
                label="Your Question",
                placeholder="e.g., 'Analyze Tesla' or 'SWOT for NVDA'",
                lines=2
            )

            chat_button = gr.Button("🚀 Ask Agent", variant="primary", size="lg")

            chat_output = gr.Textbox(
                label="Agent Response",
                lines=25,
                max_lines=30,
                show_copy_button=True
            )

            chat_button.click(
                fn=smart_agent,
                inputs=[chat_input],
                outputs=[chat_output]
            )

        # Tab 2: Manual Selection
        with gr.Tab("📊 Manual Selection"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Select or Enter Company")

                    sector_dropdown = gr.Dropdown(
                        choices=list(POPULAR_TICKERS.keys()),
                        label="Sector (Optional)",
                        value=None
                    )

                    company_dropdown = gr.Dropdown(
                        choices=[],
                        label="Popular Companies",
                        value=None
                    )

                    ticker_input = gr.Textbox(
                        label="Or Enter Ticker Symbol",
                        placeholder="e.g., AAPL, MSFT, GOOGL",
                        max_lines=1
                    )

                    analysis_type = gr.Radio(
                        choices=["Financial Metrics", "M&A Analysis", "SWOT Analysis"],
                        label="Analysis Type",
                        value="Financial Metrics"
                    )

                    analyze_btn = gr.Button("🚀 Analyze", variant="primary", size="lg")

                with gr.Column(scale=2):
                    output = gr.Textbox(
                        label="Analysis Results",
                        lines=25,
                        max_lines=30,
                        show_copy_button=True
                    )

            # Event handlers
            sector_dropdown.change(
                fn=update_companies,
                inputs=[sector_dropdown],
                outputs=[company_dropdown]
            )

            company_dropdown.change(
                fn=lambda x: x if x else "",
                inputs=[company_dropdown],
                outputs=[ticker_input]
            )

            analyze_btn.click(
                fn=analyze_company,
                inputs=[ticker_input, analysis_type],
                outputs=[output]
            )

    gr.Markdown("""
    ---
    **Data Source:** Yahoo Finance API | **Built for:** Databricks Hackathon
    """)

# Launch app
if __name__ == "__main__":
    try:
        print("Starting Financial Analyst Agent (CLEAN VERSION)...")
        print("Using direct Yahoo Finance API - NO yfinance dependency")
        print("Server: 0.0.0.0:8000")
        app.launch(
            server_name="0.0.0.0",
            server_port=8000,
            share=False,
            show_error=True,
            quiet=False
        )
    except Exception as e:
        print(f"Error launching app: {e}")
        import traceback
        traceback.print_exc()
        raise
