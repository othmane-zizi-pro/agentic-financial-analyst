"""
Fixed Setup script for Databricks Financial Analyst Agent
Run this in a Databricks notebook - FIXED for Repos environment
"""

# COMMAND ----------
# MAGIC %md
# MAGIC # Financial Analyst Agent Setup (Fixed)
# MAGIC
# MAGIC This notebook sets up the Financial Analyst Agent on Databricks
# MAGIC
# MAGIC ## Prerequisites
# MAGIC - Databricks workspace with Foundation Model API access
# MAGIC - Cluster with runtime DBR 14.3 LTS ML or higher
# MAGIC - GitHub repo connected via Repos (already done!)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1: Install Required Libraries

# COMMAND ----------
# Install required packages
%pip install mlflow>=2.10.0 langchain>=0.1.0 langchain-community>=0.0.20 databricks-sdk>=0.18.0
%pip install yfinance>=0.2.36 pandas>=2.0.0 requests>=2.31.0
%pip install beautifulsoup4>=4.12.0 gradio>=4.19.0
%pip install databricks-agents pydantic>=2.0.0

# Restart Python to use newly installed packages
dbutils.library.restartPython()

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2: Verify Databricks Environment

# COMMAND ----------
import os
import sys
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

# Get current user
current_user = w.current_user.me()
print(f"✓ Connected as: {current_user.user_name}")

# Get notebook path (we're running from Repos)
notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
print(f"✓ Notebook path: {notebook_path}")

# Determine repo root (go up from current location)
# Path will be like: /Repos/user@email.com/agentic-financial-analyst/setup_databricks_fixed
repo_root = "/".join(notebook_path.split("/")[:-1])
print(f"✓ Repo root: {repo_root}")

# Add to Python path
sys.path.insert(0, f"/Workspace{repo_root}")
print(f"✓ Added to Python path: /Workspace{repo_root}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3: Test the Agent Tools

# COMMAND ----------
# Import and test tools
from financial_agent.tools import get_financial_metrics_tool, get_ma_tool, get_swot_tool

print("✓ Tools imported successfully")

# Test financial metrics tool
print("\n" + "="*70)
print("Testing Financial Metrics Tool with Apple (AAPL)")
print("="*70)

financial_tool = get_financial_metrics_tool()
result = financial_tool(ticker="AAPL", metrics_type="summary")
print(result[:500] + "..." if len(result) > 500 else result)

print("\n✓ Financial metrics tool working!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4: Test M&A Analyzer

# COMMAND ----------
print("Testing M&A Analyzer with Microsoft (MSFT)")
print("="*70)

ma_tool = get_ma_tool()
result = ma_tool(ticker="MSFT")
print(result[:500] + "..." if len(result) > 500 else result)

print("\n✓ M&A analyzer working!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 5: Test SWOT Analyzer

# COMMAND ----------
print("Testing SWOT Analyzer with Tesla (TSLA)")
print("="*70)

swot_tool = get_swot_tool()
result = swot_tool(ticker="TSLA")
print(result[:500] + "..." if len(result) > 500 else result)

print("\n✓ SWOT analyzer working!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 6: Initialize the Agent with Databricks Foundation Model

# COMMAND ----------
from financial_agent.agent import create_financial_agent

# Create agent instance
# Available models: databricks-dbrx-instruct, databricks-meta-llama-3-70b-instruct, etc.
try:
    agent = create_financial_agent(
        model_name="databricks-dbrx-instruct",
        temperature=0.1,
        max_tokens=2000
    )
    print("✓ Agent created successfully with DBRX-Instruct model")

except Exception as e:
    print(f"⚠ Could not create agent with Foundation Model: {e}")
    print("\nNote: Make sure you have access to Databricks Foundation Model API")
    print("You can still use the tools directly without the full agent")
    agent = None

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 7: Test Agent Query

# COMMAND ----------
# Test a simple query
if agent is not None:
    print("Testing agent query...")

    response = agent.query("What are the key financial metrics for Microsoft (MSFT)?")

    print("\n" + "="*70)
    print("AGENT RESPONSE:")
    print("="*70)
    print(response.get("output", "No output"))

    if response.get("success"):
        print("\n✓ Agent query successful!")
    else:
        print("\n⚠ Agent query failed:", response.get("error"))
else:
    print("⚠ Agent not available - skipping query test")
    print("You can still use the individual tools!")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 8: Log Agent to MLflow (Optional)

# COMMAND ----------
import mlflow

# Set MLflow experiment
experiment_name = f"/Users/{current_user.user_name}/financial-analyst-agent"
mlflow.set_experiment(experiment_name)

if agent is not None:
    with mlflow.start_run(run_name="financial_analyst_v1") as run:
        # Log parameters
        mlflow.log_param("model_name", "databricks-dbrx-instruct")
        mlflow.log_param("temperature", 0.1)
        mlflow.log_param("num_tools", 3)

        # Log the agent
        try:
            mlflow.langchain.log_model(
                agent.agent_executor,
                "financial_analyst_agent",
                input_example={"input": "Analyze Apple's financial metrics"}
            )
            print(f"✓ Agent logged to MLflow")
            print(f"  Experiment: {experiment_name}")
            print(f"  Run ID: {run.info.run_id}")

        except Exception as e:
            print(f"⚠ Could not log to MLflow: {e}")
else:
    print("⚠ Skipping MLflow logging (agent not available)")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 9: Launch UI (Optional - Test in Notebook)

# COMMAND ----------
# Uncomment to test the Gradio UI in the notebook
# Note: This will open the UI inline in the notebook

# from financial_agent.ui import launch_app
#
# print("Launching Financial Analyst UI...")
# print("The app will appear below")
#
# # Launch app inline in notebook
# launch_app(share=False, server_port=7860)

# COMMAND ----------
# MAGIC %md
# MAGIC ## ✅ Setup Complete!
# MAGIC
# MAGIC ### What's Working:
# MAGIC - ✅ All three tools (Financial Metrics, M&A, SWOT)
# MAGIC - ✅ Agent with Foundation Model (if available)
# MAGIC - ✅ MLflow tracking (if agent available)
# MAGIC
# MAGIC ### Next Steps:
# MAGIC
# MAGIC #### Option 1: Use Tools Directly
# MAGIC ```python
# MAGIC from financial_agent.tools import get_financial_metrics_tool
# MAGIC
# MAGIC tool = get_financial_metrics_tool()
# MAGIC result = tool(ticker="AAPL", metrics_type="summary")
# MAGIC print(result)
# MAGIC ```
# MAGIC
# MAGIC #### Option 2: Use the Agent
# MAGIC ```python
# MAGIC from financial_agent.agent import create_financial_agent
# MAGIC
# MAGIC agent = create_financial_agent()
# MAGIC response = agent.query("Analyze Tesla's financial performance")
# MAGIC print(response["output"])
# MAGIC ```
# MAGIC
# MAGIC #### Option 3: Deploy as Databricks App
# MAGIC 1. Go to **Apps** in Databricks
# MAGIC 2. Click **Create App**
# MAGIC 3. Select **From Git**
# MAGIC 4. Choose your repo: `agentic-financial-analyst`
# MAGIC 5. Select `app.yaml`
# MAGIC 6. Click **Create**
# MAGIC 7. Wait 2-3 minutes
# MAGIC 8. Click **Open App**
# MAGIC
# MAGIC ---
# MAGIC **Setup Complete!** 🎉
