# 🚨 RENDER DEPLOYMENT - API KEY SETUP GUIDE

## Problem
Your logs show: `API Key not found. Please pass a valid API key.`

This means the Google API keys are **NOT set in Render's environment**.

---

## ✅ SOLUTION: Add Environment Variables in Render Dashboard

### Step 1: Access Render Dashboard
1. Go to: https://dashboard.render.com
2. Select your service: **ai-agentic-honeypot-system**
3. Click **"Environment"** in the left sidebar

### Step 2: Add Environment Variables

**IMPORTANT:** The `render.yaml` file has `sync: false` for all API keys. This means you **MUST manually add them** in the dashboard.

Add these variables ONE BY ONE:

```bash
# Required: API Key for authentication
API_KEY=honeypot-secret-2026

# Required: LLM Provider
LLM_PROVIDER=gemini

# Required: Google API Keys (ADD ALL 10)
GOOGLE_API_KEY=AIzaSyBFagfSKwSupA9CKDbvDKB7MuhLhzMsc3Q
GOOGLE_API_KEY_2=AIzaSyClwAyKKQQwny2cnuJtZrqGJX9e6uy25s0
GOOGLE_API_KEY_3=AIzaSyAqyskyGiO_W2sulGt5rgd2kRpqKtIppkw
GOOGLE_API_KEY_4=AIzaSyB_utyys4t4pgfy963N9XQdmfa9tOfJOaU
GOOGLE_API_KEY_5=AIzaSyD81wLwL38FUQBoLqryrIS_of-tz4L9FvI
GOOGLE_API_KEY_6=AIzaSyBgc1l9u-uwHMHNKEcPWWJBZRuUn7qzeMk
GOOGLE_API_KEY_7=AIzaSyDfJUgLV12EpMge0Kc5QEoljvck7eLQcCc
GOOGLE_API_KEY_8=AIzaSyAJSsczAaVJHqdU4LcEvXs2Tf23Qo3jBn4
GOOGLE_API_KEY_9=AIzaSyC1GB9J_XAQwgt3QlvCkXseg1-zXyccasU
GOOGLE_API_KEY_10=AIzaSyACrmRuwxg1P6f_Ee386YSZrxubJW5i73o

# Required: Gemini Model
GEMINI_MODEL=models/gemini-2.5-flash

# Optional: Anthropic (Backup)
ANTHROPIC_API_KEY=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
ANTHROPIC_MODEL=claude-haiku-4.5-20250110

# Performance Settings
LLM_MAX_TOKENS_DETECTION=1500
LLM_MAX_TOKENS_RESPONSE=2000

# Other Settings (copy from RENDER_ENV_VARIABLES.txt)
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
SESSION_TIMEOUT_MINUTES=30
MAX_MESSAGES_PER_SESSION=50
CACHE_MAX_SIZE=1000
LLM_REQUEST_TIMEOUT=5
ENABLE_FAST_PATH=true
FAST_PATH_THRESHOLD=6
SCAM_DETECTION_THRESHOLD=0.5
SCAM_SCORE_THRESHOLD=2
INCLUDE_DEBUG_INFO=false
USE_REDIS=false
```

### Step 3: Mark Sensitive Keys as Secret

For each API key, click the **eye icon** (👁️) to mark it as "Secret":
- `API_KEY`
- `ANTHROPIC_API_KEY`
- All `GOOGLE_API_KEY*` variables

### Step 4: Save and Deploy

1. Click **"Save Changes"** button
2. Render will automatically **redeploy** your service
3. Wait 2-3 minutes for deployment to complete

---

## 🔍 Verify the Fix

After redeployment, check the logs:

### ✅ Success - You should see:
```
✅ AI Agent: 10 Gemini API key(s) initialized
🚀 AI Agent: Claude Haiku 4.5 initialized
```

### ❌ Still failing - You'll see:
```
❌ API Key not found. Please pass a valid API key.
```

---

## 🧪 Test Locally First

Before deploying, test locally:

```bash
# Run diagnostic script
python check_env.py

# Expected output:
# ✅ Found 10 key(s)
# ✅ All checks passed!
```

---

## 🔑 API Key Troubleshooting

### Issue 1: Keys not loading in Render

**Cause:** Environment variables not set in dashboard

**Fix:**
1. Go to Render Dashboard → Environment
2. Manually add each variable (KEY = VALUE)
3. Don't forget the underscore in `GOOGLE_API_KEY_2`, `GOOGLE_API_KEY_3`, etc.

### Issue 2: Invalid API Keys

**Cause:** Keys are expired or incorrect

**Fix:**
1. Generate new Google API keys at: https://makersuite.google.com/app/apikey
2. Update keys in Render Dashboard
3. Redeploy

### Issue 3: Key rotation not working

**Cause:** Only some keys are invalid

**Fix:**
1. Run `python check_env.py` to identify which keys work
2. Remove invalid keys from Render
3. Add valid replacement keys

---

## 📋 Quick Copy-Paste for Render

Use this format in Render Dashboard:

| Key | Value |
|-----|-------|
| `API_KEY` | `honeypot-secret-2026` |
| `LLM_PROVIDER` | `gemini` |
| `GOOGLE_API_KEY` | `AIzaSyBFagfSKwSupA9CKDbvDKB7MuhLhzMsc3Q` |
| `GOOGLE_API_KEY_2` | `AIzaSyClwAyKKQQwny2cnuJtZrqGJX9e6uy25s0` |
| `GOOGLE_API_KEY_3` | `AIzaSyAqyskyGiO_W2sulGt5rgd2kRpqKtIppkw` |
| ... | *(continue for all 10 keys)* |

---

## 💡 Pro Tips

1. **Test API keys first**: Use the diagnostic script before deploying
2. **Use key rotation**: Having 10 keys helps avoid rate limits
3. **Monitor logs**: Watch for "API Key not found" errors
4. **Keep backups**: Save your working `.env` file locally

---

## 🆘 Still Not Working?

1. Delete ALL environment variables in Render
2. Add them again one by one
3. Make sure there are no typos in variable NAMES
4. Ensure there are no extra spaces in VALUES
5. Redeploy after each change

---

## 📞 Need Help?

Check the logs after deployment:
```bash
# In Render Dashboard → Logs tab
# Look for:
✅ AI Agent: X Gemini API key(s) initialized
```

If you see `0` keys, the environment variables are not set correctly.
