# Pre-Deployment Checklist

## ✅ Code Readiness

### Backend
- [x] `api/index.py` - Vercel handler configured
- [x] `vercel.json` - Configuration file present
- [x] `requirements.txt` - All dependencies listed (no mangum, no boto3)
- [x] All routes registered in `app/main.py`
- [x] Database models defined
- [x] Groq API integration complete
- [x] CORS middleware configured

### Frontend
- [x] `vercel.json` - Configuration file present
- [x] API client configured (`src/lib/api.ts`)
- [x] Builder page connected to backend
- [x] All UI components present
- [x] Environment variable handling in place

## 📋 Environment Variables Required

### Backend (Set in Vercel Dashboard)
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:YOUR_DATABASE_PASSWORD@ep-icy-rice-ahq4erv1-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
LLAMA_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_API_KEY=your_groq_api_key_here
CORS_ORIGINS=https://placeholder.com
APP_NAME=EU ForecastHUB API
API_PREFIX=/api/v1
```

### Frontend (Set in Vercel Dashboard)
```
VITE_API_BASE_URL=https://your-backend.vercel.app/api/v1
```

## 🔍 Pre-Deployment Verification

1. **Backend Structure:**
   - ✅ `api/index.py` exists and exports `handler`
   - ✅ `app/main.py` exists and creates FastAPI app
   - ✅ All route modules exist: forecasts, collaborations, uploads, builder, dbn
   - ✅ `requirements.txt` is complete

2. **Frontend Structure:**
   - ✅ `package.json` has all dependencies
   - ✅ `vercel.json` configured for Vite
   - ✅ `src/lib/api.ts` handles environment variables
   - ✅ All pages and components exist

3. **Configuration Files:**
   - ✅ `vercel.json` in both projects
   - ✅ `.vercelignore` in backend (excludes unnecessary files)
   - ✅ `.gitignore` properly configured

## 🚀 Deployment Steps

1. Push backend to GitHub
2. Deploy backend to Vercel (with env vars)
3. Push frontend to GitHub
4. Deploy frontend to Vercel (with VITE_API_BASE_URL)
5. Update backend CORS_ORIGINS with frontend URL

## ✅ Post-Deployment Testing

After deployment, test these endpoints:

- [ ] `GET /api/v1/health` - Should return `{"success":true,"data":{"status":"ok"}}`
- [ ] `POST /api/v1/builder/run` - Should accept requests
- [ ] `POST /api/v1/dbn/build` - Should accept spec and return model_spec_id
- [ ] Frontend loads without errors
- [ ] Builder page connects to backend
- [ ] No CORS errors in browser console

## 🐛 Common Issues to Watch For

1. **Import Errors:**
   - Check all imports in `api/index.py`
   - Verify `app.main.create_app` exists

2. **Database Connection:**
   - Verify DATABASE_URL is correct
   - Check Neon database allows external connections

3. **CORS Errors:**
   - Ensure CORS_ORIGINS includes frontend URL exactly
   - Check for trailing slashes

4. **Environment Variables:**
   - VITE_API_BASE_URL must be set before building frontend
   - All backend env vars must be set in Vercel dashboard

## 📝 Notes

- Vercel Hobby plan has 10-second function timeout
- DBN training might timeout if longer than 10 seconds
- Consider Pro plan (60-second timeout) if needed

