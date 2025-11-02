# Required Changes for Vercel Deployment

## ✅ Everything You Need to Change

### 1. Environment Variables in Vercel Dashboard

Go to **Vercel Dashboard → Your Project → Settings → Environment Variables** and set:

```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
LLAMA_API_URL=http://163.192.42.252:11434/api/generate
LLAMA_MODEL=llama3:8b
LLAMA_API_KEY=
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

**Key Points:**
- ✅ **DATABASE_URL**: Must be PostgreSQL (NOT SQLite). Use Neon, Supabase, or any PostgreSQL provider.
- ✅ **LLAMA_API_URL**: Points to your Lambda GPU instance
- ✅ **LLAMA_MODEL**: Set to `llama3:8b` for Ollama
- ✅ **CORS_ORIGINS**: Update with your actual frontend URL after frontend deployment

### 2. No Code Changes Needed! ✅

**All code is already ready:**
- ✅ `JSONType` adapter automatically uses JSONB for PostgreSQL and JSON for SQLite
- ✅ Ollama API integration already implemented in `llama_client.py`
- ✅ Database initialization works automatically on startup
- ✅ `vercel.json` configuration is correct
- ✅ `api/index.py` handler is properly configured

### 3. What Happens Automatically

When you deploy to Vercel:

1. **Database Type Detection**: The `JSONType` adapter in `app/core/database.py` automatically detects PostgreSQL from `DATABASE_URL` and uses JSONB
2. **LLaMA API**: The `llama_client.py` detects Ollama endpoint (`/api/generate` or port `11434`) and uses the correct format
3. **Database Initialization**: Tables are created automatically on first request via `init_models()` in startup event

### 4. Deployment Steps

1. **Push code to GitHub** (already done ✅)
2. **Connect to Vercel:**
   - Go to https://vercel.com/new
   - Import from GitHub → Select your repo → `backend` branch
   - Framework: **Other**
   - Build Command: `pip install -r requirements.txt`

3. **Add Environment Variables** (see #1 above)

4. **Deploy**

### 5. Post-Deployment Testing

```bash
# Test health
curl https://YOUR_BACKEND_URL.vercel.app/api/v1/health

# Test DBN query (should work with your Lambda instance)
curl -X POST https://YOUR_BACKEND_URL.vercel.app/api/v1/dbn/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A drought is forming in southern Europe"}'
```

## 🎯 Summary

**What to change:**
- ❌ Nothing in code!
- ✅ Only environment variables in Vercel Dashboard

**What works automatically:**
- ✅ PostgreSQL vs SQLite detection
- ✅ JSONB vs JSON type selection
- ✅ Ollama API format detection
- ✅ Database initialization

**What you need:**
- ✅ PostgreSQL database (Neon/Supabase)
- ✅ Lambda instance accessible from internet
- ✅ Environment variables set in Vercel

That's it! 🚀

