# 🚀 Quick Start - Deploy in 5 Minutes

## Option 1: Deploy to Vercel (Recommended)

### Step 1: Push to GitHub
```bash
git push origin HEAD:main
```

### Step 2: Deploy to Vercel

**Using Vercel CLI:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Add your OpenRouter API key
vercel env add OPENROUTER_API_KEY
# Paste: your-openrouter-api-key-here

# Deploy to production
vercel --prod
```

**Using Vercel Dashboard:**
1. Go to https://vercel.com/new
2. Import your GitHub repo: `waleed260/code_debugger`
3. Add environment variable:
   - Name: `OPENROUTER_API_KEY`
   - Value: `your-openrouter-api-key-here`
4. Click "Deploy"

### Step 3: Test Your Deployment

Visit: `https://your-app.vercel.app`

You'll see a beautiful web interface where you can:
- Paste error traces
- Get AI-powered debugging analysis
- See comprehensive reports from 3 AI agents

---

## Option 2: Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export OPENROUTER_API_KEY="your-openrouter-api-key-here"

# Run the API
python api/index.py

# Open browser
open http://localhost:5000
```

---

## 🎯 What You Get

### Web Interface
- Beautiful, modern UI
- Paste error traces and get instant analysis
- Real-time debugging with 3 AI agents
- Comprehensive reports with quality scores

### API Endpoints
- `GET /` - Web interface
- `GET /health` - Health check
- `POST /debug` - Debug errors
- `GET /api/agents` - Agent info

### AI Agents
1. **Debug Sleuth** - Root cause analysis (10x deeper)
2. **Solution Architect** - Fix generation (3 approaches)
3. **Reliability Engineer** - Validation (0-100 scoring)

---

## 📊 Example Usage

### Web Interface
1. Visit your deployed URL
2. Paste your error trace
3. Click "Analyze Error"
4. Get comprehensive debugging report

### API
```bash
curl -X POST https://your-app.vercel.app/debug \
  -H "Content-Type: application/json" \
  -d '{
    "error_trace": "Traceback (most recent call last):\n  File \"app.py\", line 42\n    item = items[index]\nIndexError: list index out of range",
    "failing_file": "app.py",
    "failing_line": 42
  }'
```

---

## 🎉 You're Done!

Your enterprise-grade debugging system is now live with:
- ✅ 10x deeper analysis
- ✅ Multiple solution approaches
- ✅ Comprehensive security audits
- ✅ Production-ready validation
- ✅ Beautiful web interface
- ✅ RESTful API

---

## 📚 Documentation

- **Full Deployment Guide**: See `VERCEL_DEPLOYMENT.md`
- **API Documentation**: See `API.md`
- **Agent Enhancements**: See `AGENT_ENHANCEMENTS.md`
- **README**: See `README.md`

---

## 🆘 Need Help?

- **Vercel Issues**: Check Vercel logs with `vercel logs`
- **API Issues**: Test with `curl https://your-app.vercel.app/health`
- **GitHub Issues**: https://github.com/waleed260/code_debugger/issues

---

**Deploy now and start debugging with AI! 🚀**
