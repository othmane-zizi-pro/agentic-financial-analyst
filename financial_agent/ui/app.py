"""
Databricks App UI for Financial Analyst Agent
Built with Gradio for interactive company analysis
"""
import gradio as gr
import sys
import os

# Add parent directory to path to import agent
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agent import create_financial_agent
from tools import get_financial_metrics_tool, get_ma_tool, get_swot_tool


# Popular company tickers for quick selection
POPULAR_TICKERS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA", "AMD", "TSLA", "AMZN"],
    "Finance": ["JPM", "BAC", "WFC", "GS", "MS", "C", "V", "MA"],
    "Healthcare": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "TMO", "DHR", "CVS"],
    "Consumer": ["WMT", "HD", "NKE", "MCD", "SBUX", "COST", "TGT", "LOW"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO"],
    "Industrial": ["CAT", "BA", "GE", "HON", "UPS", "LMT", "DE", "MMM"]
}


class FinancialAnalystUI:
    """UI wrapper for the Financial Analyst Agent"""

    def __init__(self):
        """Initialize the UI with agent and tools"""
        self.agent = None
        self.financial_tool = get_financial_metrics_tool()
        self.ma_tool = get_ma_tool()
        self.swot_tool = get_swot_tool()

        # Initialize agent (lazy loading to avoid initialization errors)
        try:
            self.agent = create_financial_agent()
        except Exception as e:
            print(f"Warning: Could not initialize agent: {e}")
            print("Direct tool access will be used instead")

    def get_financial_metrics(self, ticker: str, metrics_type: str = "summary") -> str:
        """Get financial metrics for a company"""
        if not ticker:
            return "Please enter a stock ticker symbol (e.g., AAPL, MSFT)"

        return self.financial_tool(ticker=ticker.upper(), metrics_type=metrics_type)

    def get_ma_analysis(self, ticker: str) -> str:
        """Get M&A analysis for a company"""
        if not ticker:
            return "Please enter a stock ticker symbol (e.g., AAPL, MSFT)"

        return self.ma_tool(ticker=ticker.upper())

    def get_swot_analysis(self, ticker: str) -> str:
        """Get SWOT analysis for a company"""
        if not ticker:
            return "Please enter a stock ticker symbol (e.g., AAPL, MSFT)"

        return self.swot_tool(ticker=ticker.upper())

    def chat_with_agent(self, message: str, history: list) -> tuple:
        """
        Chat with the financial analyst agent

        Args:
            message: User message
            history: Chat history

        Returns:
            Tuple of (updated history, empty string for clearing input)
        """
        if not message:
            return history, ""

        # Add user message to history
        history.append({"role": "user", "content": message})

        try:
            if self.agent:
                # Use the agent for comprehensive analysis
                response = self.agent.query(message)
                agent_response = response.get("output", "No response generated")
            else:
                # Fallback: Parse user intent and call tools directly
                agent_response = self._fallback_response(message)

            # Add agent response to history
            history.append({"role": "assistant", "content": agent_response})

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history.append({"role": "assistant", "content": error_msg})

        return history, ""

    def _fallback_response(self, message: str) -> str:
        """Fallback response when agent is not available"""
        message_lower = message.lower()

        # Try to extract ticker from message
        words = message.upper().split()
        potential_tickers = [w for w in words if len(w) <= 5 and w.isalpha()]

        if not potential_tickers:
            return """I can help you analyze companies! Please provide a stock ticker symbol (e.g., AAPL, MSFT, GOOGL).

I can provide:
- Financial metrics and ratios
- M&A activity analysis
- SWOT analysis

Try asking: "Analyze AAPL" or "What are the financial metrics for Microsoft?"
"""

        ticker = potential_tickers[0]

        # Determine what analysis to provide
        if any(word in message_lower for word in ["swot", "strengths", "weaknesses", "opportunities", "threats"]):
            return self.get_swot_analysis(ticker)
        elif any(word in message_lower for word in ["m&a", "merger", "acquisition", "ma activity"]):
            return self.get_ma_analysis(ticker)
        else:
            # Default to financial metrics
            return self.get_financial_metrics(ticker, metrics_type="summary")

    def create_ui(self) -> gr.Blocks:
        """Create the Gradio UI"""

        with gr.Blocks(
            title="Financial Analyst Agent",
            theme=gr.themes.Soft()
        ) as app:

            gr.Markdown("""
            # 📊 Financial Analyst Agent
            ### Powered by Databricks Mosaic AI

            Get comprehensive financial analysis for any publicly traded company including:
            - Real-time financial metrics and ratios
            - M&A activity analysis
            - SWOT analysis with strategic insights
            """)

            with gr.Tabs():
                # Tab 1: Quick Analysis
                with gr.Tab("🔍 Quick Analysis"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### Select or Enter Company")

                            # Sector dropdown
                            sector_dropdown = gr.Dropdown(
                                choices=list(POPULAR_TICKERS.keys()),
                                label="Sector (Optional)",
                                value=None
                            )

                            # Company dropdown (populated based on sector)
                            company_dropdown = gr.Dropdown(
                                choices=[],
                                label="Popular Companies",
                                value=None
                            )

                            # Or enter custom ticker
                            ticker_input = gr.Textbox(
                                label="Or Enter Ticker Symbol",
                                placeholder="e.g., AAPL, MSFT, GOOGL",
                                max_lines=1
                            )

                            # Analysis type
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

                    # Update company dropdown when sector changes
                    def update_companies(sector):
                        if sector:
                            return gr.update(choices=POPULAR_TICKERS[sector], value=None)
                        return gr.update(choices=[], value=None)

                    sector_dropdown.change(
                        fn=update_companies,
                        inputs=[sector_dropdown],
                        outputs=[company_dropdown]
                    )

                    # Set ticker input when company selected from dropdown
                    def set_ticker(company):
                        return company if company else ""

                    company_dropdown.change(
                        fn=set_ticker,
                        inputs=[company_dropdown],
                        outputs=[ticker_input]
                    )

                    # Analysis function
                    def run_analysis(ticker, analysis_type):
                        if not ticker:
                            return "Please select or enter a company ticker symbol"

                        if analysis_type == "Financial Metrics":
                            return self.get_financial_metrics(ticker, "summary")
                        elif analysis_type == "M&A Analysis":
                            return self.get_ma_analysis(ticker)
                        elif analysis_type == "SWOT Analysis":
                            return self.get_swot_analysis(ticker)

                    analyze_btn.click(
                        fn=run_analysis,
                        inputs=[ticker_input, analysis_type],
                        outputs=[output]
                    )

                # Tab 2: AI Chat Interface
                with gr.Tab("💬 Chat with AI Analyst"):
                    gr.Markdown("""
                    ### Interactive Financial Analysis
                    Ask questions in natural language and get comprehensive analysis from our AI agent.

                    **Example questions:**
                    - "What are the key financial metrics for Apple?"
                    - "Analyze Tesla's M&A activity"
                    - "Give me a SWOT analysis for Microsoft"
                    - "Compare Amazon and Walmart"
                    """)

                    chatbot = gr.Chatbot(
                        label="Financial Analyst",
                        height=500,
                        type="messages"
                    )

                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your Question",
                            placeholder="Ask me anything about company financials...",
                            scale=4,
                            max_lines=3
                        )
                        submit_btn = gr.Button("Send", variant="primary", scale=1)

                    clear_btn = gr.Button("Clear Chat")

                    # Chat handlers
                    submit_btn.click(
                        fn=self.chat_with_agent,
                        inputs=[msg, chatbot],
                        outputs=[chatbot, msg]
                    )

                    msg.submit(
                        fn=self.chat_with_agent,
                        inputs=[msg, chatbot],
                        outputs=[chatbot, msg]
                    )

                    clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg])

                # Tab 3: Detailed Metrics
                with gr.Tab("📈 Detailed Metrics"):
                    with gr.Row():
                        with gr.Column():
                            detail_ticker = gr.Textbox(
                                label="Ticker Symbol",
                                placeholder="e.g., AAPL"
                            )

                            metrics_type = gr.Radio(
                                choices=["summary", "ratios", "historical", "detailed"],
                                label="Metrics Detail Level",
                                value="summary"
                            )

                            detail_btn = gr.Button("Get Detailed Metrics", variant="primary")

                        with gr.Column():
                            detail_output = gr.Textbox(
                                label="Detailed Financial Metrics",
                                lines=25,
                                show_copy_button=True
                            )

                    detail_btn.click(
                        fn=self.get_financial_metrics,
                        inputs=[detail_ticker, metrics_type],
                        outputs=[detail_output]
                    )

            gr.Markdown("""
            ---
            **Data Sources:** Yahoo Finance, Public Market Data
            **Powered by:** Databricks Mosaic AI Agent Framework
            """)

        return app


def launch_app(share: bool = False, server_port: int = 7860):
    """
    Launch the Databricks Financial Analyst App

    Args:
        share: Whether to create a public share link
        server_port: Port to run the server on
    """
    ui = FinancialAnalystUI()
    app = ui.create_ui()

    app.launch(
        share=share,
        server_port=server_port,
        server_name="0.0.0.0",  # Allow external connections
        show_error=True
    )


if __name__ == "__main__":
    # Launch the app
    launch_app(share=False, server_port=7860)
