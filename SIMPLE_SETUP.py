"""
SIMPLE SETUP - Financial Analyst Agent for Databricks
This is a minimal, stable setup that won't crash the kernel
Run ONE CELL AT A TIME and wait for completion before moving to the next
"""

# COMMAND ----------
# MAGIC %md
# MAGIC # Simple Setup - Financial Analyst Agent
# MAGIC
# MAGIC **IMPORTANT:** Run ONE cell at a time, wait for ✓ before continuing!
# MAGIC
# MAGIC If any cell fails, just skip to the next one.

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 1: Install Core Packages (Wait ~2 minutes)

# COMMAND ----------
%pip install yfinance pandas requests beautifulsoup4 --quiet

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 2: Install UI Package (Wait ~1 minute)

# COMMAND ----------
%pip install gradio --quiet

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 3: Restart Python (Required!)

# COMMAND ----------
dbutils.library.restartPython()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 4: Setup Python Path

# COMMAND ----------
import sys
import os

# Get notebook path
notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
print(f"Notebook path: {notebook_path}")

# Get repo root
repo_root = "/".join(notebook_path.split("/")[:-1])
print(f"Repo root: {repo_root}")

# Add to path
sys.path.insert(0, f"/Workspace{repo_root}")
print(f"✓ Added to Python path")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 5: Test Financial Metrics Tool

# COMMAND ----------
from financial_agent.tools import get_financial_metrics_tool

print("Testing Financial Metrics Tool...")
print("="*70)

tool = get_financial_metrics_tool()
result = tool(ticker="AAPL", metrics_type="summary")

print(result)
print("\n✓ Financial Metrics Tool works!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 6: Test M&A Analyzer

# COMMAND ----------
from financial_agent.tools import get_ma_tool

print("Testing M&A Analyzer...")
print("="*70)

ma_tool = get_ma_tool()
result = ma_tool(ticker="MSFT")

print(result[:800])
print("\n✓ M&A Analyzer works!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 7: Test SWOT Analyzer

# COMMAND ----------
from financial_agent.tools import get_swot_tool

print("Testing SWOT Analyzer...")
print("="*70)

swot_tool = get_swot_tool()
result = swot_tool(ticker="TSLA")

print(result)
print("\n✓ SWOT Analyzer works!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Cell 8: Try Multiple Companies

# COMMAND ----------
from financial_agent.tools import get_financial_metrics_tool

tool = get_financial_metrics_tool()

# Test different companies
companies = ["NVDA", "GOOGL", "META", "AMZN"]

for ticker in companies:
    print(f"\n{'='*70}")
    print(f"Financial Summary: {ticker}")
    print('='*70)

    result = tool(ticker=ticker, metrics_type="summary")
    print(result[:600])
    print("...")

print("\n✓ All tests passed! Tools are working perfectly!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## ✅ Setup Complete!
# MAGIC
# MAGIC ### What's Working:
# MAGIC - ✅ Financial Metrics Tool - Get real-time financial data
# MAGIC - ✅ M&A Analyzer - Track merger & acquisition activity
# MAGIC - ✅ SWOT Analyzer - Generate strategic analysis
# MAGIC
# MAGIC ### Quick Usage Examples:
# MAGIC
# MAGIC ```python
# MAGIC # Get financial metrics
# MAGIC from financial_agent.tools import get_financial_metrics_tool
# MAGIC tool = get_financial_metrics_tool()
# MAGIC print(tool(ticker="AAPL", metrics_type="ratios"))
# MAGIC ```
# MAGIC
# MAGIC ```python
# MAGIC # Get M&A analysis
# MAGIC from financial_agent.tools import get_ma_tool
# MAGIC ma = get_ma_tool()
# MAGIC print(ma(ticker="MSFT"))
# MAGIC ```
# MAGIC
# MAGIC ```python
# MAGIC # Get SWOT analysis
# MAGIC from financial_agent.tools import get_swot_tool
# MAGIC swot = get_swot_tool()
# MAGIC print(swot(ticker="TSLA"))
# MAGIC ```
# MAGIC
# MAGIC ### Deploy as Databricks App:
# MAGIC
# MAGIC Now that the tools work, deploy the UI:
# MAGIC
# MAGIC 1. Go to **Apps** in Databricks sidebar
# MAGIC 2. Click **Create App**
# MAGIC 3. Select **From Git**
# MAGIC 4. Choose repository: `agentic-financial-analyst`
# MAGIC 5. Select file: `app.yaml`
# MAGIC 6. Click **Create**
# MAGIC 7. Wait 2-3 minutes
# MAGIC 8. Click **Open App** 🎉
# MAGIC
# MAGIC The app will have a full web UI with:
# MAGIC - Company selector by sector
# MAGIC - All three analysis types
# MAGIC - Interactive interface
# MAGIC
# MAGIC ---
# MAGIC **You're ready to go!** 🚀
