# Quick Start Guide - Financial Analyst Agent

Get your Financial Analyst Agent running on Databricks in **15 minutes**!

## Prerequisites
- Databricks workspace with Foundation Model API access
- GitHub connected to Databricks (or ability to upload files)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Get the Code into Databricks (2 minutes)

**Option A: Using GitHub (Recommended)**
```bash
# 1. Push this code to your GitHub
git init
git add .
git commit -m "Financial analyst agent"
git remote add origin <your-repo-url>
git push -u origin main

# 2. In Databricks: Workspace > Repos > Add Repo
# - Connect GitHub and clone your repo
```

**Option B: Direct Upload**
```bash
# Use Databricks CLI
databricks workspace import-dir . /Workspace/Users/<your-email>/databricks-hackathon
```

---

### Step 2: Create a Cluster (3 minutes)

1. Go to **Compute** > **Create Cluster**
2. Configure:
   - **Name:** `financial-agent-cluster`
   - **Runtime:** `14.3 LTS ML` or higher
   - **Node Type:** `i3.xlarge` (or smallest available)
   - **Workers:** Autoscaling 1-2
3. Click **Create Cluster** and wait ~3 minutes

---

### Step 3: Run Setup Notebook (10 minutes)

1. Open `setup_databricks.py` in your workspace
2. Attach to your cluster
3. **Run all cells** (⌘/Ctrl + Shift + Enter)
4. Wait for setup to complete

The notebook will:
- ✅ Install dependencies (~2 min)
- ✅ Test all tools (~1 min)
- ✅ Create agent (~2 min)
- ✅ Log to MLflow (~1 min)
- ✅ Ready to use! (~5 min total)

---

## 🎯 Test It Out!

### Test in Notebook
```python
from agent import create_financial_agent

# Create agent
agent = create_financial_agent()

# Ask a question
response = agent.query("What are Apple's key financial metrics?")
print(response["output"])
```

### Launch UI
```python
from ui import launch_app

# Start Gradio interface
launch_app(share=False, server_port=7860)
# Click the link to open UI
```

---

## 📊 Try These Example Queries

**Financial Metrics:**
- "What are the financial metrics for Tesla?"
- "Show me Microsoft's profitability ratios"
- "Compare Apple and Amazon's valuations"

**M&A Analysis:**
- "Analyze recent M&A activity for JPMorgan"
- "What mergers has Microsoft been involved in?"

**SWOT Analysis:**
- "Generate a SWOT analysis for NVIDIA"
- "What are Tesla's strengths and weaknesses?"

---

## 🚢 Deploy as Databricks App (Optional)

Want a persistent web app everyone can access?

### 1. Create App (2 minutes)
```bash
# In Databricks UI:
# Apps > Create App > From Git
# - Select your repo
# - Choose app.yaml
# - Click Deploy
```

### 2. Access App
- Wait 2-3 minutes for deployment
- Click **Open App** to launch
- Share URL with your team!

---

## 💡 What You Can Do

### Quick Analysis Tab
1. Select a sector (Technology, Finance, etc.)
2. Choose a company or enter ticker
3. Pick analysis type (Metrics, M&A, SWOT)
4. Click **Analyze** 🚀

### Chat Interface
- Ask questions in natural language
- Get comprehensive analysis
- Interactive conversation with AI

### Detailed Metrics
- Deep dive into financial ratios
- Historical performance data
- Custom metric selections

---

## 🎓 Tips for Success

### Optimize Costs
```python
# Enable auto-suspend in app.yaml
auto_suspend:
  enabled: true
  idle_timeout_minutes: 30
```

### Popular Companies by Sector
- **Tech:** AAPL, MSFT, GOOGL, META, NVDA
- **Finance:** JPM, BAC, GS, V, MA
- **Healthcare:** JNJ, UNH, PFE, ABBV
- **Consumer:** WMT, AMZN, HD, NKE

### Get Better Responses
- Always use stock ticker symbols (AAPL not "Apple")
- Be specific in your questions
- Try multiple analysis types for comprehensive view

---

## ❌ Troubleshooting

**"Cannot connect to Foundation Model"**
→ Make sure your workspace has Foundation Model API enabled

**"Module not found"**
→ Run `%pip install -r requirements.txt` and restart Python

**"No data for ticker"**
→ Verify ticker symbol is correct (use Yahoo Finance to check)

**App won't deploy**
→ Check app.yaml syntax and file paths

---

## 📈 What's Next?

1. **Customize Company Lists**
   - Edit `POPULAR_TICKERS` in `financial_agent/ui/app.py`
   - Add your favorite companies

2. **Enhance with More Data**
   - Get free Alpha Vantage API key
   - Add to Databricks secrets
   - More comprehensive financial data!

3. **Advanced Features**
   - Multi-company comparison
   - Portfolio analysis
   - Automated reports
   - Email alerts

4. **Share with Team**
   - Set app permissions
   - Create user guide
   - Collect feedback

---

## 🎉 You're Ready!

Your Financial Analyst Agent is now running on Databricks!

**Helpful Resources:**
- 📖 [Full Deployment Guide](DEPLOYMENT_GUIDE.md)
- 📘 [Databricks Agent Framework Docs](https://docs.databricks.com/en/generative-ai/agent-framework/)
- 💬 Need help? Check the troubleshooting section or Databricks docs

**Happy Analyzing! 📊💹**
