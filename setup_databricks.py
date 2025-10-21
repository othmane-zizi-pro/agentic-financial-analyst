"""
Setup script for Databricks Financial Analyst Agent
Run this in a Databricks notebook to set up the agent
"""

# COMMAND ----------
# MAGIC %md
# MAGIC # Financial Analyst Agent Setup
# MAGIC
# MAGIC This notebook sets up the Financial Analyst Agent on Databricks
# MAGIC
# MAGIC ## Prerequisites
# MAGIC - Databricks workspace with Foundation Model API access
# MAGIC - Cluster with runtime DBR 14.3 LTS ML or higher
# MAGIC - GitHub repo connected (optional, for version control)

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
from databricks.sdk import WorkspaceClient

# Initialize Databricks client
w = WorkspaceClient()

# Get current user
current_user = w.current_user.me()
print(f"✓ Connected as: {current_user.user_name}")

# Check for Foundation Model API access
try:
    endpoints = w.serving_endpoints.list()
    print(f"✓ Serving endpoints accessible: {len(list(endpoints))} endpoints found")
except Exception as e:
    print(f"⚠ Warning: Could not access serving endpoints: {e}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3: Clone or Sync GitHub Repository

# COMMAND ----------
# If using GitHub integration, sync the repo
# Otherwise, upload the financial_agent folder to your workspace

import subprocess
import sys

# Set your repo path
REPO_PATH = "/Workspace/Users/" + current_user.user_name + "/databricks-hackathon"

# Create directory if it doesn't exist
dbutils.fs.mkdirs(f"file:{REPO_PATH}")

print(f"✓ Workspace path ready: {REPO_PATH}")
print("\nIf using GitHub:")
print("  1. Go to Workspace > Repos in your Databricks workspace")
print("  2. Click 'Add Repo' and connect your GitHub account")
print("  3. Clone the databricks-hackathon repository")
print("\nOtherwise:")
print("  Upload the financial_agent folder to this workspace")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4: Test the Agent Tools

# COMMAND ----------
# Add the financial_agent package to Python path
sys.path.append(f"{REPO_PATH}/financial_agent")

# Test importing tools
from tools import get_financial_metrics_tool, get_ma_tool, get_swot_tool

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
# MAGIC ## Step 5: Initialize the Agent with Databricks Foundation Model

# COMMAND ----------
from agent import create_financial_agent

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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 6: Test Agent Query

# COMMAND ----------
# Test a simple query
if 'agent' in locals():
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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 7: Log Agent to MLflow

# COMMAND ----------
import mlflow

# Set MLflow experiment
experiment_name = f"/Users/{current_user.user_name}/financial-analyst-agent"
mlflow.set_experiment(experiment_name)

if 'agent' in locals():
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

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 8: Register Model

# COMMAND ----------
# Register the model for deployment
if 'agent' in locals():
    try:
        model_name = "financial_analyst_agent"

        # Register model
        model_uri = f"runs:/{run.info.run_id}/financial_analyst_agent"
        model_version = mlflow.register_model(model_uri, model_name)

        print(f"✓ Model registered: {model_name}")
        print(f"  Version: {model_version.version}")

    except Exception as e:
        print(f"⚠ Could not register model: {e}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 9: Launch Databricks App UI

# COMMAND ----------
# Note: This cell will start the Gradio app
# You can access it via the notebook output or deploy as a Databricks App

from ui import launch_app

print("Launching Financial Analyst UI...")
print("The app will be available at the URL shown below")
print("\nTo deploy as a Databricks App:")
print("  1. Go to Workspace > Apps")
print("  2. Create New App")
print("  3. Select this notebook or app.py")
print("  4. Configure compute and deploy")

# Launch app (comment out if deploying as separate app)
# launch_app(share=False, server_port=7860)

# COMMAND ----------
# MAGIC %md
# MAGIC ## Next Steps
# MAGIC
# MAGIC ### Option 1: Run in Notebook
# MAGIC - Uncomment the `launch_app()` call above
# MAGIC - Run the cell to start the Gradio interface
# MAGIC
# MAGIC ### Option 2: Deploy as Databricks App
# MAGIC 1. Create `app.yaml` in your repo:
# MAGIC ```yaml
# MAGIC command: ["python", "financial_agent/ui/app.py"]
# MAGIC env:
# MAGIC   - name: DATABRICKS_HOST
# MAGIC     value: "{{ workspace.host }}"
# MAGIC   - name: DATABRICKS_TOKEN
# MAGIC     value: "{{ secrets.default.databricks_token }}"
# MAGIC ```
# MAGIC
# MAGIC 2. In Databricks UI: Apps > Create App
# MAGIC 3. Select your repo and app.yaml
# MAGIC 4. Deploy!
# MAGIC
# MAGIC ### Option 3: Model Serving Endpoint
# MAGIC Deploy the MLflow model as a serving endpoint for API access
# MAGIC
# MAGIC ---
# MAGIC **Setup Complete!** 🎉
