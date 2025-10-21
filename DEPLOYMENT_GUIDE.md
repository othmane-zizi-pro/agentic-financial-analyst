# Deployment Guide - Financial Analyst Agent on Databricks

## Overview
This guide walks you through deploying the Financial Analyst Agent to your Databricks workspace.

## Prerequisites

✅ **Required:**
- Databricks workspace with $600 credits (as mentioned)
- Access to Databricks Foundation Model API (DBRX-Instruct or Llama models)
- Cluster with DBR 14.3 LTS ML or higher
- GitHub account connected to Databricks (recommended)

✅ **Optional:**
- Alpha Vantage API key (for enhanced financial data - free tier available)
- Databricks secrets for API keys

---

## Deployment Options

### Option 1: Quick Start - Databricks Notebook (Recommended for Testing)

**Best for:** Testing and experimentation

1. **Upload Files to Workspace**
   ```bash
   # From your local machine
   databricks workspace import-dir \
     /Users/othmanezizi/databricks-hackathon \
     /Workspace/Users/<your-email>/databricks-hackathon
   ```

2. **Create a Cluster**
   - Go to Compute > Create Cluster
   - Runtime: **14.3 LTS ML** or higher
   - Node type: `i3.xlarge` or similar (optimize for cost)
   - Enable autoscaling: 1-2 workers

3. **Run Setup Notebook**
   - Open `setup_databricks.py` in your workspace
   - Attach to your cluster
   - Run all cells sequentially
   - The notebook will:
     - Install dependencies
     - Test tools
     - Initialize agent
     - Log to MLflow
     - Launch UI (optional)

4. **Access the UI**
   - After running the last cell, click the Gradio link
   - Or deploy as a separate app (see Option 2)

**Estimated Credit Usage:** ~$2-5 for testing session

---

### Option 2: Databricks App (Recommended for Production)

**Best for:** Persistent, shareable application

1. **Connect GitHub Repo**
   ```bash
   # Push your code to GitHub
   cd /Users/othmanezizi/databricks-hackathon
   git init
   git add .
   git commit -m "Initial commit: Financial Analyst Agent"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Connect Repo in Databricks**
   - Workspace > Repos > Add Repo
   - Connect GitHub account
   - Clone your repository

3. **Create App Configuration**

   Create `app.yaml` in repo root:
   ```yaml
   name: financial-analyst-agent
   description: AI-powered financial analyst for company analysis

   command:
     - python
     - financial_agent/ui/app.py

   resources:
     compute:
       size: SMALL

   env:
     - name: DATABRICKS_HOST
       valueFrom:
         workspace: host
     - name: DATABRICKS_TOKEN
       valueFrom:
         secret:
           scope: default
           key: databricks_token
   ```

4. **Create Databricks Secret (if needed)**
   ```bash
   # Install Databricks CLI
   pip install databricks-cli

   # Configure
   databricks configure --token

   # Create secret scope
   databricks secrets create-scope --scope default

   # Add token
   databricks secrets put --scope default --key databricks_token
   ```

5. **Deploy App**
   - Go to **Workspace > Apps** in Databricks UI
   - Click **Create App**
   - Select **From Git**
   - Choose your repository
   - Select `app.yaml`
   - Click **Deploy**
   - Wait 2-3 minutes for deployment

6. **Access Your App**
   - Apps > Your App > Open
   - Share URL with team members
   - Set permissions as needed

**Estimated Credit Usage:** ~$10-20/day for continuous operation

---

### Option 3: Model Serving Endpoint (API Access)

**Best for:** Programmatic access, integration with other apps

1. **Register Model** (done in setup notebook)
   ```python
   # Already completed in setup_databricks.py
   mlflow.register_model(model_uri, "financial_analyst_agent")
   ```

2. **Create Serving Endpoint**
   - Go to **Machine Learning > Serving**
   - Click **Create Serving Endpoint**
   - Name: `financial-analyst-agent`
   - Model: Select `financial_analyst_agent` (latest version)
   - Compute: **Small** (for cost efficiency)
   - Scale to zero: **Enabled** (save credits)
   - Click **Create**

3. **Test Endpoint**
   ```python
   import requests
   import os

   url = "https://<workspace-url>/serving-endpoints/financial-analyst-agent/invocations"
   headers = {
       "Authorization": f"Bearer {os.environ['DATABRICKS_TOKEN']}",
       "Content-Type": "application/json"
   }

   data = {
       "inputs": {
           "input": "What are the financial metrics for Apple?"
       }
   }

   response = requests.post(url, headers=headers, json=data)
   print(response.json())
   ```

**Estimated Credit Usage:** ~$5-15/day (depends on query volume, scale-to-zero helps)

---

## Step-by-Step: Recommended Deployment Path

### Phase 1: Development & Testing (Days 1-2)
- [ ] Clone repo to Databricks workspace
- [ ] Create development cluster
- [ ] Run `setup_databricks.py` notebook
- [ ] Test all three tools (metrics, M&A, SWOT)
- [ ] Test agent with sample queries
- [ ] Verify MLflow logging

**Budget: ~$10-15**

### Phase 2: UI Development (Days 3-4)
- [ ] Launch Gradio UI from notebook
- [ ] Test all UI tabs (Quick Analysis, Chat, Detailed Metrics)
- [ ] Customize company list for your use case
- [ ] Test with various companies and sectors
- [ ] Gather feedback from team

**Budget: ~$15-20**

### Phase 3: Production Deployment (Days 5-6)
- [ ] Create `app.yaml` configuration
- [ ] Deploy as Databricks App
- [ ] Set up permissions and sharing
- [ ] Create user documentation
- [ ] Monitor credit usage

**Budget: ~$20-30/day for continuous operation**

### Phase 4: Optimization (Days 7+)
- [ ] Enable app auto-suspend when idle
- [ ] Optimize cluster size based on usage
- [ ] Add caching for frequent queries
- [ ] Consider batch processing for reports
- [ ] Set up monitoring and alerts

**Ongoing Budget: ~$10-20/day optimized**

---

## Cost Optimization Tips

1. **Use Scale-to-Zero**
   - Enable for serving endpoints
   - Set app to suspend after 30 minutes idle

2. **Right-Size Compute**
   - Start with Small compute
   - Use spot instances where possible
   - Enable autoscaling with min=1

3. **Cache Results**
   - Implement caching for financial data (updates needed)
   - Use Delta tables for historical data

4. **Batch Operations**
   - Group multiple queries
   - Schedule reports during off-peak hours

5. **Monitor Usage**
   ```sql
   -- Check credit usage
   SELECT
     usage_date,
     sku_name,
     usage_quantity,
     usage_unit
   FROM
     system.billing.usage
   WHERE
     usage_date >= current_date() - INTERVAL 7 DAYS
   ORDER BY
     usage_date DESC
   ```

---

## Troubleshooting

### Issue: "Cannot connect to Foundation Model API"
**Solution:**
- Verify your workspace has Foundation Model API enabled
- Try alternative model: `databricks-meta-llama-3-70b-instruct`
- Contact Databricks support to enable access

### Issue: "Module not found" errors
**Solution:**
```python
# Run in notebook cell
%pip install --upgrade mlflow langchain databricks-sdk
dbutils.library.restartPython()
```

### Issue: "Rate limit exceeded" from Yahoo Finance
**Solution:**
- Implement caching (see cache example below)
- Add rate limiting between requests
- Consider paid data provider

### Issue: App deployment fails
**Solution:**
- Check `app.yaml` syntax
- Verify all file paths are correct
- Check cluster has required libraries
- Review app logs in Databricks UI

---

## Monitoring & Maintenance

### Track Agent Performance
```python
# Add to your code
import mlflow

with mlflow.start_run():
    result = agent.query(user_input)

    # Log metrics
    mlflow.log_metric("response_time", response_time)
    mlflow.log_metric("tokens_used", tokens)
    mlflow.log_param("user_query", user_input)
```

### Monitor Credit Usage
- Set up billing alerts in Databricks
- Review usage weekly
- Optimize based on patterns

### Update Agent
```bash
# Pull latest changes
cd databricks-hackathon
git pull origin main

# Redeploy app
databricks apps deploy
```

---

## Next Steps

1. **Enhance Data Sources**
   - Add Alpha Vantage API for more data
   - Integrate SEC EDGAR for filings
   - Add real-time news feeds

2. **Advanced Features**
   - Multi-company comparison
   - Portfolio analysis
   - Automated report generation
   - Email/Slack alerts

3. **Scale**
   - Deploy multiple instances
   - Add load balancing
   - Implement user authentication

---

## Support

- **Databricks Docs:** https://docs.databricks.com
- **Agent Framework:** https://docs.databricks.com/en/generative-ai/agent-framework/
- **MLflow:** https://mlflow.org/docs/latest/index.html

**Your $600 credit budget breakdown:**
- Development & Testing: $25-50
- 2 weeks production usage: $140-280
- Buffer for experimentation: $270-435

This should give you **2-3 weeks of active development and testing** or **4-6 weeks of optimized production use**.

Good luck with your hackathon! 🚀
