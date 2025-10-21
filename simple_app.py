"""
Simple Databricks App for Financial Analyst
Uses standalone tools with no complex dependencies
"""
import gradio as gr
import yfinance as yf
from typing import Dict, Any
from datetime import datetime

# ============================================================================
# STANDALONE TOOLS (Copied inline to avoid import issues)
# ============================================================================

class FinancialMetricsTool:
    """Standalone financial metrics tool"""

    def __call__(self, ticker: str, metrics_type: str = "summary") -> str:
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            if metrics_type == "summary":
                return self._get_summary(info, ticker.upper())
            elif metrics_type == "ratios":
                return self._get_ratios(info, ticker.upper())
            else:
                return self._get_summary(info, ticker.upper())

        except Exception as e:
            return f"Error fetching data for {ticker}: {str(e)}"

    def _get_summary(self, info: Dict, ticker: str) -> str:
        output = f"Financial Metrics for {ticker}\n"
        output += "=" * 70 + "\n\n"

        output += f"Company: {info.get('longName', 'N/A')}\n"
        output += f"Sector: {info.get('sector', 'N/A')}\n"
        output += f"Industry: {info.get('industry', 'N/A')}\n\n"

        # Market data
        market_cap = info.get('marketCap', 0)
        if market_cap > 1_000_000_000:
            market_cap_str = f"${market_cap / 1_000_000_000:.2f}B"
        else:
            market_cap_str = f"${market_cap / 1_000_000:.2f}M"

        output += f"Market Cap: {market_cap_str}\n"
        output += f"Current Price: ${info.get('currentPrice', 'N/A')}\n"
        output += f"52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
        output += f"52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}\n\n"

        # Valuation
        output += "Valuation Metrics:\n"
        output += f"  P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
        output += f"  Forward P/E: {info.get('forwardPE', 'N/A')}\n"
        output += f"  Price to Book: {info.get('priceToBook', 'N/A')}\n"
        output += f"  PEG Ratio: {info.get('pegRatio', 'N/A')}\n\n"

        # Profitability
        output += "Profitability:\n"
        profit_margin = info.get('profitMargins', 0)
        operating_margin = info.get('operatingMargins', 0)
        output += f"  Profit Margin: {profit_margin * 100:.2f}%\n" if profit_margin else "  Profit Margin: N/A\n"
        output += f"  Operating Margin: {operating_margin * 100:.2f}%\n" if operating_margin else "  Operating Margin: N/A\n"
        output += f"  ROE: {info.get('returnOnEquity', 'N/A')}\n"
        output += f"  ROA: {info.get('returnOnAssets', 'N/A')}\n\n"

        # Growth
        revenue_growth = info.get('revenueGrowth', 0)
        output += "Growth:\n"
        output += f"  Revenue Growth: {revenue_growth * 100:.2f}%\n" if revenue_growth else "  Revenue Growth: N/A\n"
        output += f"  Earnings Growth: {info.get('earningsGrowth', 'N/A')}\n\n"

        # Financial Health
        output += "Financial Health:\n"
        output += f"  Current Ratio: {info.get('currentRatio', 'N/A')}\n"
        output += f"  Debt to Equity: {info.get('debtToEquity', 'N/A')}\n"
        output += f"  Quick Ratio: {info.get('quickRatio', 'N/A')}\n\n"

        # Analyst Opinion
        output += f"Analyst Recommendation: {info.get('recommendationKey', 'N/A').upper()}\n"

        return output

    def _get_ratios(self, info: Dict, ticker: str) -> str:
        output = f"Financial Ratios for {ticker}\n"
        output += "=" * 70 + "\n\n"

        output += "Profitability Ratios:\n"
        output += f"  Gross Margin: {info.get('grossMargins', 'N/A')}\n"
        output += f"  Operating Margin: {info.get('operatingMargins', 'N/A')}\n"
        output += f"  Profit Margin: {info.get('profitMargins', 'N/A')}\n"
        output += f"  ROE: {info.get('returnOnEquity', 'N/A')}\n"
        output += f"  ROA: {info.get('returnOnAssets', 'N/A')}\n\n"

        output += "Valuation Ratios:\n"
        output += f"  P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
        output += f"  Forward P/E: {info.get('forwardPE', 'N/A')}\n"
        output += f"  PEG Ratio: {info.get('pegRatio', 'N/A')}\n"
        output += f"  Price to Book: {info.get('priceToBook', 'N/A')}\n"
        output += f"  Price to Sales: {info.get('priceToSalesTrailing12Months', 'N/A')}\n\n"

        output += "Liquidity Ratios:\n"
        output += f"  Current Ratio: {info.get('currentRatio', 'N/A')}\n"
        output += f"  Quick Ratio: {info.get('quickRatio', 'N/A')}\n\n"

        output += "Leverage Ratios:\n"
        output += f"  Debt to Equity: {info.get('debtToEquity', 'N/A')}\n"

        return output


class MATool:
    """Standalone M&A analysis tool"""

    def __call__(self, ticker: str) -> str:
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            output = f"M&A Activity Analysis for {ticker.upper()}\n"
            output += "=" * 70 + "\n\n"

            output += f"Company: {info.get('longName', 'N/A')}\n"
            output += f"Sector: {info.get('sector', 'N/A')}\n"
            output += f"Industry: {info.get('industry', 'N/A')}\n\n"

            # Get news
            news = ticker_obj.news if hasattr(ticker_obj, 'news') else []

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


class SWOTTool:
    """Standalone SWOT analysis tool"""

    def __call__(self, ticker: str) -> str:
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            output = f"SWOT Analysis for {ticker.upper()}\n"
            output += "=" * 70 + "\n\n"

            output += f"Company: {info.get('longName', 'N/A')}\n"
            output += f"Sector: {info.get('sector', 'N/A')}\n"
            output += f"Industry: {info.get('industry', 'N/A')}\n\n"

            output += "=" * 70 + "\n\n"

            # STRENGTHS
            output += "STRENGTHS\n"
            output += "-" * 70 + "\n"

            strengths = []
            if info.get('profitMargins', 0) > 0.15:
                strengths.append(f"Strong profit margin of {info.get('profitMargins', 0) * 100:.1f}%")
            if info.get('returnOnEquity', 0) > 0.15:
                strengths.append(f"Excellent ROE of {info.get('returnOnEquity', 0) * 100:.1f}%")
            if info.get('currentRatio', 0) > 1.5:
                strengths.append(f"Healthy liquidity with current ratio of {info.get('currentRatio', 0):.2f}")
            if info.get('revenueGrowth', 0) > 0.1:
                strengths.append(f"Strong revenue growth of {info.get('revenueGrowth', 0) * 100:.1f}%")

            if not strengths:
                strengths.append("Established market presence")

            for i, s in enumerate(strengths, 1):
                output += f"{i}. {s}\n"

            # WEAKNESSES
            output += "\nWEAKNESSES\n"
            output += "-" * 70 + "\n"

            weaknesses = []
            if info.get('debtToEquity', 0) > 2.0:
                weaknesses.append(f"High debt-to-equity ratio of {info.get('debtToEquity', 0):.2f}")
            if info.get('currentRatio', 0) < 1.0 and info.get('currentRatio', 0) > 0:
                weaknesses.append(f"Low liquidity with current ratio of {info.get('currentRatio', 0):.2f}")
            if info.get('trailingPE', 0) > 30:
                weaknesses.append(f"High P/E ratio of {info.get('trailingPE', 0):.2f} may indicate overvaluation")

            if not weaknesses:
                weaknesses.append("Limited public data available")

            for i, w in enumerate(weaknesses, 1):
                output += f"{i}. {w}\n"

            # OPPORTUNITIES
            output += "\nOPPORTUNITIES\n"
            output += "-" * 70 + "\n"

            opportunities = []
            if info.get('revenueGrowth', 0) > 0:
                opportunities.append("Continue expanding in growing markets")
            if info.get('pegRatio', 0) < 1.0 and info.get('pegRatio', 0) > 0:
                opportunities.append("Potential undervaluation based on growth")

            opportunities.append(f"Leverage position in {info.get('industry', 'the industry')}")

            for i, o in enumerate(opportunities, 1):
                output += f"{i}. {o}\n"

            # THREATS
            output += "\nTHREATS\n"
            output += "-" * 70 + "\n"

            threats = []
            if info.get('beta', 0) > 1.5:
                threats.append(f"High market volatility (beta: {info.get('beta', 0):.2f})")
            if info.get('debtToEquity', 0) > 1.5:
                threats.append("Elevated debt levels")

            threats.append(f"Competition in {info.get('industry', 'the industry')}")
            threats.append("Market volatility")

            for i, t in enumerate(threats, 1):
                output += f"{i}. {t}\n"

            output += "\n" + "=" * 70 + "\n"

            return output

        except Exception as e:
            return f"Error generating SWOT for {ticker}: {str(e)}"


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


# Create Gradio interface
with gr.Blocks(title="Financial Analyst Agent", theme=gr.themes.Soft()) as app:

    gr.Markdown("""
    # 📊 Financial Analyst Agent
    ### Powered by Databricks

    Get real-time financial analysis for any publicly traded company.
    """)

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
    **Data Source:** Yahoo Finance | **Built for:** Databricks Hackathon
    """)

# Launch app
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=8080)
