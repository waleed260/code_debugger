
# Vercel Deployment Guide

## 🚀 Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (free tier works)
- OpenRouter API key

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin HEAD:main
```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

4. Add environment variable:
```bash
vercel env add OPENROUTER_API_KEY
# Paste your API key when prompted
```

5. Redeploy with environment variable:
```bash
vercel --prod
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: (leave empty)
   - **Output Directory**: public

5. Add Environment Variables:
   - Click "Environment Variables"
   - Add: `OPENROUTER_API_KEY` = `your-api-key-here`
   - Add: `OPENROUTER_BASE_URL` = `https://openrouter.ai/api/v1`
   - Add: `OPENROUTER_MODEL` = `gpt-3.5-turbo`

6. Click "Deploy"

### Step 3: Test Your Deployment

Once deployed, you'll get a URL like: `https://your-app.vercel.app`

Test the API:

```bash
# Health check
curl https://your-app.vercel.app/health

# Debug an error
curl -X POST https://your-app.vercel.app/debug \
  -H "Content-Type: application/json" \
  -d '{
    "error_trace": "Traceback (most recent call last):\n  File \"app.py\", line 42\n    item = items[index]\nIndexError: list index out of range",
    "failing_file": "app.py",
    "failing_line": 42
  }'
```

Or visit the web interface:
```
https://your-app.vercel.app
```

---

## 📁 Project Structure

```
code_debugger/
├── api/
│   └── index.py          # Flask API (Vercel serverless function)
├── public/
│   └── index.html        # Web interface
├── src/
│   └── code_debugger/    # Core debugging agents
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🔧 Configuration

### vercel.json
- Defines build settings
- Routes requests to API
- Sets environment variables

### Environment Variables
Required:
- `OPENROUTER_API_KEY` - Your OpenRouter API key

Optional:
- `OPENROUTER_BASE_URL` - API endpoint (default: https://openrouter.ai/api/v1)
- `OPENROUTER_MODEL` - Model to use (default: gpt-3.5-turbo)

---

## 🌐 API Endpoints

### GET /
Web interface (HTML)

### GET /health
Health check
```json
{
  "status": "healthy",
  "service": "code-debugger",
  "version": "2.0"
}
```

### POST /debug
Debug an error
```json
{
  "error_trace": "...",
  "failing_file": "app.py",
  "failing_line": 42
}
```

### GET /api/agents
Get agent information

---

## 🐛 Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility (3.12+)

### API Returns 500
- Check Vercel logs: `vercel logs`
- Verify environment variables are set
- Check OpenRouter API key is valid

### Timeout Errors
- Vercel free tier has 10s timeout for serverless functions
- Consider upgrading to Pro for 60s timeout
- Or optimize agent prompts for faster responses

---

## 💰 Cost Considerations

### Vercel
- **Free Tier**: 100GB bandwidth, 100 serverless function invocations/day
- **Pro**: $20/month - More bandwidth and invocations

### OpenRouter
- **gpt-3.5-turbo**: ~$0.002 per request
- **gpt-4o**: ~$0.03 per request
- Free tier available with limited credits

---

## 🔒 Security

- API key stored as Vercel environment variable (encrypted)
- Not exposed in client-side code
- CORS enabled for web interface
- Rate limiting recommended for production

---

## 📊 Monitoring

View logs:
```bash
vercel logs
```

View analytics:
- Go to Vercel dashboard
- Select your project
- Click "Analytics"

---

## 🚀 Next Steps

1. **Custom Domain**: Add your own domain in Vercel settings
2. **Rate Limiting**: Add rate limiting for production use
3. **Authentication**: Add API key authentication for public APIs
4. **Monitoring**: Set up error tracking (Sentry, etc.)
5. **Caching**: Add caching for repeated queries

---

## 📞 Support

- **Vercel Docs**: https://vercel.com/docs
- **OpenRouter Docs**: https://openrouter.ai/docs
- **Issues**: https://github.com/waleed260/code_debugger/issues

---

**Your debugging agent is now live! 🎉**
