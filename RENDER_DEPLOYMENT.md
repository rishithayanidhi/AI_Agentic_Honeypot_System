# 🚀 Render Deployment Guide - AI Agentic Honeypot

## Quick Deploy to Render

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for Render deployment with unlimited Gemini keys"
git push origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 3: Deploy from GitHub

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Render will auto-detect the `render.yaml` file

### Step 4: Configure Environment Variables

Render will automatically load most settings from `render.yaml`, but you need to add your **secret keys** in the Render Dashboard:

#### Required Variables (Add in Render Dashboard):

```
API_KEY=honeypot-secret-2026
```

#### Choose Your LLM Provider:

**Option A: Anthropic (Claude) - Recommended**

```
ANTHROPIC_API_KEY=your-anthropic-api-key-here
LLM_PROVIDER=anthropic
```

**Option B: Google Gemini with UNLIMITED Keys**

```
GOOGLE_API_KEY=your-first-gemini-key
GOOGLE_API_KEY_2=your-second-gemini-key
GOOGLE_API_KEY_3=your-third-gemini-key
GOOGLE_API_KEY_4=your-fourth-gemini-key
GOOGLE_API_KEY_5=your-fifth-gemini-key
... add as many as you want!
LLM_PROVIDER=gemini
```

**Option C: OpenAI (GPT)**

```
OPENAI_API_KEY=your-openai-api-key-here
LLM_PROVIDER=openai
```

### Adding Unlimited Gemini Keys

The system automatically detects **all** environment variables matching `GOOGLE_API_KEY*` pattern.

#### To add more Gemini keys:

1. Go to Render Dashboard → Your Service → **Environment**
2. Click **Add Environment Variable**
3. Add keys following the pattern:
   - `GOOGLE_API_KEY_5`
   - `GOOGLE_API_KEY_6`
   - `GOOGLE_API_KEY_7`
   - ... continue as needed

4. Click **Save Changes**
5. Render will automatically redeploy

**No code changes required!** The system will automatically detect and use all keys for rotation.

### Step 5: Deploy

1. Click **Create Web Service**
2. Render will:
   - Install dependencies from `requirements.txt`
   - Start the server with `uvicorn`
   - Provide a public URL: `https://your-app.onrender.com`

### Step 6: Verify Deployment

Test the health endpoint:

```bash
curl https://your-app.onrender.com/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2026-02-16T...",
  "provider": "anthropic",
  "gemini_keys": 5
}
```

### Step 7: Test the API

```bash
curl -X POST https://your-app.onrender.com/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: honeypot-secret-2026" \
  -d '{
    "user_id": "test_user_123",
    "session_id": "test_session_456",
    "message": "Hello! You won $1,000,000! Send your bank details."
  }'
```

## Environment Variables Reference

### Required

| Variable                                | Description                | Example                |
| --------------------------------------- | -------------------------- | ---------------------- |
| `API_KEY`                               | Authentication key for API | `honeypot-secret-2026` |
| `ANTHROPIC_API_KEY` or `GOOGLE_API_KEY` | LLM provider key           | Your API key           |

### Optional - Gemini Keys (Unlimited)

| Variable           | Description                |
| ------------------ | -------------------------- |
| `GOOGLE_API_KEY`   | Primary Gemini key         |
| `GOOGLE_API_KEY_2` | Secondary key for rotation |
| `GOOGLE_API_KEY_3` | Third key                  |
| `GOOGLE_API_KEY_N` | Add unlimited keys         |

### Configuration

| Variable                   | Default                     | Description                              |
| -------------------------- | --------------------------- | ---------------------------------------- |
| `LLM_PROVIDER`             | `anthropic`                 | Options: `anthropic`, `gemini`, `openai` |
| `ANTHROPIC_MODEL`          | `claude-haiku-4.5-20250110` | Claude model                             |
| `GEMINI_MODEL`             | `gemini-2.0-flash-exp`      | Gemini model                             |
| `SESSION_TIMEOUT_MINUTES`  | `30`                        | Session timeout                          |
| `MAX_MESSAGES_PER_SESSION` | `50`                        | Max messages per session                 |
| `SCAM_SCORE_THRESHOLD`     | `2`                         | Scam detection threshold                 |

## Post-Deployment

### Monitor Logs

- Go to Render Dashboard → Logs
- Watch for successful startup messages
- Check for API key initialization

### Update Environment Variables

1. Render Dashboard → Environment
2. Add/Edit variables
3. Click **Save Changes** (auto-redeploys)

### Scale Up

- Render Free Tier: Sleeps after inactivity
- Paid Plans: Always-on, faster cold starts
- Add more Gemini keys for higher rate limits

## Troubleshooting

### Issue: "No LLM providers available"

**Solution**: Add at least one API key (`ANTHROPIC_API_KEY` or `GOOGLE_API_KEY`)

### Issue: Rate limit errors

**Solution**: Add more Gemini API keys (`GOOGLE_API_KEY_2`, `GOOGLE_API_KEY_3`, etc.)

### Issue: Service sleeps on free tier

**Solution**:

- Upgrade to paid plan for always-on service
- Or use a cron job to ping `/health` every 10 minutes

### Issue: Slow cold starts

**Solution**:

- Add more Gemini keys for faster failover
- Use Anthropic (Claude) for more consistent performance

## Support

- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Production Guide**: See [PRODUCTION_READY.md](PRODUCTION_READY.md)
- **API Docs**: Visit `https://your-app.onrender.com/docs`

---

✅ **Your honeypot is now live on Render with unlimited Gemini API key support!**
