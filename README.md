# Financial Analyst Agent - Databricks Hackathon

An AI-enhanced financial analyst agent that provides comprehensive company analysis with LLM-powered insights and guaranteed reliability through fallback mechanisms.

## Features

- ✅ **LLM-Enhanced Analysis** - Powered by Databricks Foundation Models (DBRX/Llama)
- ✅ **Smart Routing** - Automatically selects the right tool based on your question
- ✅ **Guaranteed Reliability** - Falls back to rules-based analysis if LLM unavailable
- ✅ **Real-time Data** - Yahoo Finance API with hardcoded fallback for 5 companies
- ✅ **Natural Language** - Ask questions using company names or ticker symbols

## Supported Analysis Types

1. **Financial Metrics** - Comprehensive financial analysis with ratios, margins, and growth metrics
2. **M&A Analysis** - Merger and acquisition activity tracking
3. **SWOT Analysis** - Strategic strengths, weaknesses, opportunities, and threats

## Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
┌──────▼──────────────┐
│  Smart Router       │ (Keyword-based routing)
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  Tool Selection     │ (Financial, M&A, or SWOT)
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  Data Fetching      │ (Yahoo Finance API → Fallback)
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  LLM Enhancement    │ (DBRX/Llama → Rules-based)
└──────┬──────────────┘
       │
┌──────▼──────────────┐
│  Final Response     │ (Shows model used)
└─────────────────────┘
```

## Technology Stack

- **LLM**: Databricks Foundation Models (DBRX-Instruct, Llama 3.1 70B)
- **UI**: Gradio
- **Data Source**: Yahoo Finance API
- **Deployment**: Databricks Apps
- **Fallback**: Hardcoded data for AAPL, MSFT, GOOGL, TSLA, NVDA

## Project Structure

```
.
├── financial_app_clean.py   # Main application with LLM enhancement
├── app.yaml                  # Databricks Apps configuration
├── start_app.sh             # Startup script with diagnostics
└── requirements.txt         # Dependencies (pandas, gradio, requests, openai)
```

## Quick Start

1. **Deploy to Databricks Apps**
   ```bash
   # App will auto-deploy from GitHub
   # Uses app.yaml configuration
   ```

2. **Try it out**
   ```
   "Analyze Tesla"
   "What are Apple's strengths and weaknesses?"
   "Show me M&A activity for Microsoft"
   "Financial ratios for Nvidia"
   ```

3. **Check the output**
   - Look for model indicator: `Model: DBRX-INSTRUCT` or `RULES-BASED`
   - LLM provides insights, risks, and recommendations
   - Fallback ensures it always works

## LLM Enhancement Details

### How it works:
1. **Try Databricks Models** (in order):
   - databricks-dbrx-instruct
   - databricks-meta-llama-3-1-70b-instruct
   - databricks-meta-llama-3-70b-instruct

2. **On Success**: Shows AI analysis with:
   - 📊 Key Insights
   - ⚠️ Risks to Watch
   - 💡 Recommendation

3. **On Failure**: Falls back to rules-based output
   - Shows: `Analysis Mode: Rules-Based (LLM unavailable)`
   - Still provides complete financial data

## Supported Companies (Guaranteed Fallback)

These companies have hardcoded data and will ALWAYS work:
- **Apple (AAPL)** - Consumer Electronics
- **Microsoft (MSFT)** - Software Infrastructure
- **Google (GOOGL)** - Internet Content
- **Tesla (TSLA)** - Auto Manufacturers
- **NVIDIA (NVDA)** - Semiconductors

## Sample Output

```
🤖 Agent Decision: Analyzing TSLA...
Tool Selected: Financial Metrics

======================================================================
Financial Metrics for TSLA
Company: Tesla, Inc.
P/E Ratio: 65.4
Profit Margin: 15%
Revenue Growth: 122%
...

======================================================================
🤖 AI-Enhanced Analysis (Model: DBRX-INSTRUCT)
======================================================================

📊 Key Insights:
1. Exceptional revenue growth of 122% signals strong market demand
2. High P/E ratio (65.4) reflects growth premium but valuation risk
3. Solid profit margins improving with scale

⚠️ Risks to Watch:
- High valuation leaves limited margin for error
- Competition intensifying in EV market

💡 Recommendation: HOLD for growth investors willing to accept
volatility. Consider trimming position if P/E exceeds 70.

======================================================================
💡 Powered by DBRX-INSTRUCT on Databricks
```

## Environment Variables (Auto-configured in Databricks Apps)

- `DATABRICKS_HOST` - Workspace host
- `DATABRICKS_CLIENT_SECRET` - Authentication token
- `GRADIO_SERVER_PORT` - Port 8000

## No Dependencies On

- ❌ yfinance (caused websockets issues)
- ❌ External API keys
- ❌ Complex frameworks
- ✅ Just pandas, gradio, requests, openai

## License

Built for Databricks Hackathon 2025
