# Financial Analyst Agent - Databricks Hackathon

An AI-powered financial analyst agent built with Databricks Mosaic AI Agent Framework that provides:
- Real-time financial metrics for companies
- M&A activity analysis among peers
- SWOT analysis using structured and unstructured data
- Interactive UI via Databricks App

## Architecture

- **Agent Framework**: Mosaic AI Agent Framework (MLflow)
- **Tools**: Financial metrics, M&A analyzer, SWOT generator
- **Data Storage**: Delta Tables on Databricks
- **LLM**: Databricks Foundation Models (DBRX-Instruct)
- **UI**: Databricks App with Gradio

## Project Structure

```
financial_agent/
├── agent/          # Agent configuration and chain logic
├── tools/          # Agent tools (financial metrics, M&A, SWOT)
├── data/           # Data fetching and processing
├── ui/             # Databricks App UI
└── config/         # Configuration files
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure API keys in Databricks secrets
3. Deploy agent: `databricks bundle deploy`
4. Launch UI: Run the Databricks App

## Environment Variables

Set these as Databricks secrets:
- `ALPHA_VANTAGE_API_KEY` (for financial data)
- `DATABRICKS_TOKEN` (for Databricks API access)
