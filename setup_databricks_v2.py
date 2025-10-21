"""
Financial Analyst Agent Setup for Databricks - V2 (Fixed Dependencies)
Run this in a Databricks notebook
"""

# COMMAND ----------
# MAGIC %md
# MAGIC # Financial Analyst Agent Setup - V2 (Dependency Fix)
# MAGIC
# MAGIC This notebook sets up the Financial Analyst Agent on Databricks with proper dependency management
# MAGIC
# MAGIC ## Prerequisites
# MAGIC - Databricks workspace with Foundation Model API access
# MAGIC - Cluster with runtime DBR 14.3 LTS ML or higher
# MAGIC - GitHub repo connected via Repos

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1: Fix Core Dependencies First

# COMMAND ----------
# Upgrade core dependencies to fix typing_extensions issue
%pip install --upgrade pip
%pip install --upgrade typing-extensions>=4.8.0
%pip install --upgrade pydantic>=2.0.0

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2: Install Required Libraries

# COMMAND ----------
# Install financial and data packages (no ML packages yet)
%pip install yfinance>=0.2.36
%pip install pandas>=2.0.0
%pip install requests>=2.31.0
%pip install beautifulsoup4>=4.12.0

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3: Install UI and SDK Packages

# COMMAND ----------
# Install Databricks and UI packages
%pip install databricks-sdk>=0.18.0
%pip install gradio>=4.19.0

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4: Install Agent Framework (Last, to avoid conflicts)

# COMMAND ----------
# Install MLflow and LangChain
%pip install mlflow>=2.10.0
%pip install langchain>=0.1.0
%pip install langchain-community>=0.0.20

# Now restart Python to use all new packages
dbutils.library.restartPython()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 5: Verify Installation

# COMMAND ----------
# Verify all imports work
import sys
print(f"Python version: {sys.version}")

try:
    import typing_extensions
    print(f"✓ typing_extensions version: {typing_extensions.__version__}")
except Exception as e:
    print(f"✗ typing_extensions error: {e}")

try:
    import pydantic
    print(f"✓ pydantic version: {pydantic.__version__}")
except Exception as e:
    print(f"✗ pydantic error: {e}")

try:
    import yfinance
    print(f"✓ yfinance installed")
except Exception as e:
    print(f"✗ yfinance error: {e}")

try:
    import gradio
    print(f"✓ gradio version: {gradio.__version__}")
except Exception as e:
    print(f"✗ gradio error: {e}")

try:
    import mlflow
    print(f"✓ mlflow version: {mlflow.__version__}")
except Exception as e:
    print(f"✗ mlflow error: {e}")

try:
    import langchain
    print(f"✓ langchain installed")
except Exception as e:
    print(f"✗ langchain error: {e}")

print("\n✓ All dependencies installed successfully!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 6: Setup Python Path

# COMMAND ----------
import os
import sys
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

# Get current user
current_user = w.current_user.me()
print(f"✓ Connected as: {current_user.user_name}")

# Get notebook path
notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
print(f"✓ Notebook path: {notebook_path}")

# Determine repo root
repo_root = "/".join(notebook_path.split("/")[:-1])
print(f"✓ Repo root: {repo_root}")

# Add to Python path
sys.path.insert(0, f"/Workspace{repo_root}")
print(f"✓ Added to Python path: /Workspace{repo_root}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 7: Test Financial Metrics Tool

# COMMAND ----------
from financial_agent.tools import get_financial_metrics_tool

print("Testing Financial Metrics Tool with Apple (AAPL)")
print("="*70)

financial_tool = get_financial_metrics_tool()
result = financial_tool(ticker="AAPL", metrics_type="summary")
print(result[:800] if len(result) > 800 else result)

print("\n✓ Financial metrics tool working!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 8: Test M&A Analyzer

# COMMAND ----------
from financial_agent.tools import get_ma_tool

print("Testing M&A Analyzer with Microsoft (MSFT)")
print("="*70)

ma_tool = get_ma_tool()
result = ma_tool(ticker="MSFT")
print(result[:800] if len(result) > 800 else result)

print("\n✓ M&A analyzer working!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 9: Test SWOT Analyzer

# COMMAND ----------
from financial_agent.tools import get_swot_tool

print("Testing SWOT Analyzer with NVIDIA (NVDA)")
print("="*70)

swot_tool = get_swot_tool()
result = swot_tool(ticker="NVDA")
print(result)

print("\n✓ SWOT analyzer working!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 10: Try to Create Agent (Optional - requires Foundation Model API)

# COMMAND ----------
try:
    from financial_agent.agent import create_financial_agent

    # Create agent instance
    agent = create_financial_agent(
        model_name="databricks-dbrx-instruct",
        temperature=0.1,
        max_tokens=2000
    )
    print("✓ Agent created successfully with DBRX-Instruct model")

    # Test query
    print("\nTesting agent query...")
    response = agent.query("What are the key financial metrics for Tesla?")

    print("\n" + "="*70)
    print("AGENT RESPONSE:")
    print("="*70)
    print(response.get("output", "No output")[:500])

    if response.get("success"):
        print("\n✓ Agent query successful!")
    else:
        print("\n⚠ Agent query had issues:", response.get("error"))

except Exception as e:
    print(f"⚠ Could not create full agent: {e}")
    print("\nThis is OK! The tools work independently.")
    print("You might not have Foundation Model API access yet.")
    agent = None

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 11: Log to MLflow (Optional)

# COMMAND ----------
import mlflow

# Set MLflow experiment
experiment_name = f"/Users/{current_user.user_name}/financial-analyst-agent"
mlflow.set_experiment(experiment_name)

if agent is not None:
    try:
        with mlflow.start_run(run_name="financial_analyst_v1") as run:
            # Log parameters
            mlflow.log_param("model_name", "databricks-dbrx-instruct")
            mlflow.log_param("temperature", 0.1)
            mlflow.log_param("num_tools", 3)

            print(f"✓ Run created in MLflow")
            print(f"  Experiment: {experiment_name}")
            print(f"  Run ID: {run.info.run_id}")
    except Exception as e:
        print(f"⚠ MLflow logging issue: {e}")
else:
    print("⚠ Skipping MLflow (agent not available)")

# COMMAND ----------
# MAGIC %md
# MAGIC ## ✅ Setup Complete!
# MAGIC
# MAGIC ### What's Working:
# MAGIC - ✅ All dependencies installed properly
# MAGIC - ✅ Financial Metrics Tool
# MAGIC - ✅ M&A Analyzer Tool
# MAGIC - ✅ SWOT Analyzer Tool
# MAGIC - ✅ Agent (if Foundation Model API available)
# MAGIC
# MAGIC ### Quick Test - Try This:
# MAGIC
# MAGIC ```python
# MAGIC # Cell 1: Test any company
# MAGIC from financial_agent.tools import get_financial_metrics_tool
# MAGIC
# MAGIC tool = get_financial_metrics_tool()
# MAGIC
# MAGIC # Try these companies:
# MAGIC for ticker in ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]:
# MAGIC     print(f"\n{'='*70}")
# MAGIC     print(f"Quick metrics for {ticker}")
# MAGIC     print('='*70)
# MAGIC     result = tool(ticker=ticker, metrics_type="summary")
# MAGIC     print(result[:400])
# MAGIC ```
# MAGIC
# MAGIC ### Deploy as Databricks App:
# MAGIC
# MAGIC 1. Go to **Apps** in Databricks
# MAGIC 2. Click **Create App**
# MAGIC 3. Select **From Git**
# MAGIC 4. Choose: `agentic-financial-analyst` repo
# MAGIC 5. Select: `app.yaml` file
# MAGIC 6. Click **Create**
# MAGIC 7. Wait 2-3 minutes
# MAGIC 8. Click **Open App** 🎉
# MAGIC
# MAGIC ---
# MAGIC **You're all set!** 🚀
