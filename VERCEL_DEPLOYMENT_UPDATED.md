# Vercel Deployment Guide - Updated Configuration

This guide covers deploying the backend to Vercel with your Lambda GPU instance for LLaMA 3.

## ✅ Prerequisites

1. **Lambda GPU Instance Running**
   - LLaMA 3 API available at: `http://163.192.42.252:11434/api/generate`
   - Model: `llama3:8b`

2. **PostgreSQL Database**
   - Neon, Supabase, or any PostgreSQL provider
   - Connection string ready

3. **GitHub Repository**
   - Backend code pushed to `backend` branch

## 📋 Step 1: Configure Environment Variables in Vercel

Go to **Vercel Dashboard → Your Project → Settings → Environment Variables**

Add/Update these variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/db?sslmode=require` | **PostgreSQL connection string** (NOT SQLite) |
| `LLAMA_API_URL` | `http://163.192.42.252:11434/api/generate` | **Your Lambda GPU instance** |
| `LLAMA_MODEL` | `llama3:8b` | **Model name for Ollama** |
| `LLAMA_API_KEY` | _(leave empty)_ | Optional, not needed for Ollama |
| `GROQ_API_KEY` | _(leave empty or remove)_ | Not needed if using Ollama |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` | **Your frontend URL** (add multiple comma-separated if needed) |
| `APP_NAME` | `EU ForecastHUB API` | Optional |
| `API_PREFIX` | `/api/v1` | Optional, default |

### ⚠️ Important Notes:

1. **DATABASE_URL must be PostgreSQL** - SQLite won't work on Vercel (serverless functions are stateless)
2. **LLAMA_API_URL points to your Lambda instance** - Make sure it's accessible from the internet
3. **CORS_ORIGINS** - Update this after frontend deployment with the actual frontend URL

## 🔧 Step 2: Verify vercel.json Configuration

Your `vercel.json` should look like this:

```json
{
  "version": 2,
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "PYTHONUNBUFFERED": "1"
  },
  "buildCommand": "pip install -r requirements.txt"
}
```

✅ This is already correct in your repository.

## 🌐 Step 3: Verify Lambda Instance Accessibility

**Before deploying**, test that your Lambda instance is accessible from the internet:

```bash
# Test from your local machine
curl -X POST http://163.192.42.252:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:8b",
    "prompt": "Hello",
    "stream": false,
    "format": "json"
  }'
```

If this fails:
- Check Lambda instance firewall rules
- Ensure port 11434 is open
- Verify the instance is running and accessible

## 🚀 Step 4: Deploy to Vercel

### Option A: Via GitHub (Recommended)

1. **Push code to GitHub:**
   ```bash
   git push origin backend
   ```

2. **Connect to Vercel:**
   - Go to https://vercel.com/new
   - Import from GitHub
   - Select your repository and `backend` branch
   - Click "Import"

3. **Configure Project:**
   - **Framework Preset:** Other
   - **Root Directory:** `./`
   - **Build Command:** `pip install -r requirements.txt`
   - **Output Directory:** _(leave empty)_

4. **Add Environment Variables** (see Step 1 above)

5. **Deploy**

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Set environment variables
vercel env add DATABASE_URL
vercel env add LLAMA_API_URL
vercel env add LLAMA_MODEL
vercel env add CORS_ORIGINS
```

## ✅ Step 5: Verify Deployment

### Test Health Endpoint:

```bash
curl https://YOUR_BACKEND_URL.vercel.app/api/v1/health
```

Expected response:
```json
{"success":true,"data":{"status":"ok"}}
```

### Test DBN Query Endpoint:

```bash
curl -X POST https://YOUR_BACKEND_URL.vercel.app/api/v1/dbn/query \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A prolonged drought is forming in southern Europe"
  }'
```

Expected: Response with nodes, edges, and forecast results.

## 🔍 Troubleshooting

### Issue: Database Connection Errors

**Problem:** `UnsupportedCompilationError: Compiler can't render element of type JSONB`

**Solution:** ✅ Already fixed! The `JSONType` adapter automatically uses JSONB for PostgreSQL.

### Issue: LLaMA API Timeout

**Problem:** Requests to Lambda instance timeout

**Solutions:**
1. Check Lambda instance is running: `curl http://163.192.42.252:11434/api/generate`
2. Verify firewall allows connections from Vercel IPs
3. Check Vercel function logs: Dashboard → Functions → api/index.py → Logs

### Issue: Function Timeout (10 seconds)

**Problem:** DBN training takes longer than 10 seconds

**Solutions:**
1. Upgrade to Vercel Pro (60-second timeout)
2. Optimize pseudo-training data generation
3. Consider moving heavy operations to background jobs

### Issue: CORS Errors

**Problem:** Frontend can't connect to backend

**Solutions:**
1. Verify `CORS_ORIGINS` in Vercel environment variables
2. Check it matches your frontend URL exactly (no trailing slash)
3. Check browser console for exact error message

### Issue: Import Errors

**Problem:** `ModuleNotFoundError` in Vercel logs

**Solutions:**
1. Verify `requirements.txt` has all dependencies
2. Check `api/index.py` imports are correct
3. Ensure `app/main.py` exists and exports `create_app`

## 📊 Monitoring

After deployment:

1. **Check Vercel Logs:**
   - Dashboard → Your Project → Deployments → [Latest] → Logs
   - Or: Dashboard → Functions → api/index.py → Logs

2. **Monitor Function Performance:**
   - Dashboard → Analytics
   - Check function duration and error rates

3. **Test Endpoints:**
   - `/api/v1/health` - Should be fast (< 1s)
   - `/api/v1/dbn/query` - May take 5-15 seconds depending on LLaMA response

## 🔄 Updating Environment Variables

If you need to change environment variables after deployment:

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Update the variable value
3. Vercel will auto-redeploy, or click "Redeploy" manually
4. Test the endpoint again

## 📝 Summary of Changes from Local Dev

| Setting | Local Development | Vercel Production |
|---------|------------------|-------------------|
| **Database** | SQLite (`forecast_hub.db`) | PostgreSQL (Neon/Supabase) |
| **LLAMA_API_URL** | `http://163.192.42.252:11434/api/generate` | Same (Lambda instance) |
| **LLAMA_MODEL** | `llama3:8b` | Same |
| **JSON Type** | JSON (SQLite) | JSONB (PostgreSQL) - **Auto-handled** |
| **Database Init** | Auto on startup | Auto on startup |

## ✅ Checklist

Before deploying, ensure:

- [ ] PostgreSQL database created and connection string ready
- [ ] Lambda instance is accessible from internet
- [ ] Environment variables set in Vercel dashboard
- [ ] Code pushed to GitHub `backend` branch
- [ ] `vercel.json` is correct
- [ ] `requirements.txt` has all dependencies
- [ ] Test `/api/v1/health` endpoint works
- [ ] Test `/api/v1/dbn/query` endpoint works

## 🎉 Done!

Your backend is now deployed and ready to use. The `/api/v1/dbn/query` endpoint will:

1. Receive prompts from frontend
2. Call your Lambda GPU instance (LLaMA 3)
3. Process the response through DBN engine
4. Return forecast results

All environment configuration is handled automatically based on your Vercel environment variables!

