# Quick Start: Deploy to Vercel

## Step 1: Push Backend to GitHub

```bash
cd the-euforecast-hub-backend1.1/the-euforecast-hub-backend1.1

git init
git add .
git commit -m "Initial commit - Backend for Vercel"
git branch -M main

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/euforecast-hub-backend.git
git push -u origin main
```

## Step 2: Deploy Backend to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your `euforecast-hub-backend` repository
4. Click "Import"

### Configure Project:
- **Framework Preset:** Other
- **Root Directory:** `./` (default)
- **Build Command:** (leave empty)
- **Output Directory:** (leave empty)
- **Install Command:** `pip install -r requirements.txt`

### Add Environment Variables:
Click "Environment Variables" and add:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql+asyncpg://neondb_owner:YOUR_DATABASE_PASSWORD@ep-icy-rice-ahq4erv1-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require` |
| `LLAMA_API_URL` | `https://api.groq.com/openai/v1/chat/completions` |
| `GROQ_API_KEY` | `your_groq_api_key_here` |
| `CORS_ORIGINS` | `https://placeholder.com` (update after frontend deploy) |
| `APP_NAME` | `EU ForecastHUB API` |
| `API_PREFIX` | `/api/v1` |

5. Click "Deploy"
6. Wait 2-5 minutes
7. **Copy your backend URL** from the deployment page (e.g., `https://euforecast-hub-backend.vercel.app`)

## Step 3: Push Frontend to GitHub

```bash
cd ../../the-euforecast-hub-frontend/the-euforecast-hub-frontend

git init
git add .
git commit -m "Initial commit - Frontend for Vercel"
git branch -M main

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/euforecast-hub-frontend.git
git push -u origin main
```

## Step 4: Deploy Frontend to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your `euforecast-hub-frontend` repository
4. Click "Import"

### Configure Project:
Vercel should auto-detect Vite. If not:
- **Framework Preset:** Vite
- **Root Directory:** `./` (default)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`

### Add Environment Variable:
Click "Environment Variables" and add:

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://YOUR_BACKEND_URL.vercel.app/api/v1` |

Replace `YOUR_BACKEND_URL` with your actual backend URL from Step 2.

5. Click "Deploy"
6. Wait 2-3 minutes
7. **Copy your frontend URL** from the deployment page

## Step 5: Update Backend CORS

1. Go to your **backend** project in Vercel dashboard
2. Go to Settings → Environment Variables
3. Find `CORS_ORIGINS` and click "Edit"
4. Change value to: `https://YOUR_FRONTEND_URL.vercel.app`
   (Replace with your actual frontend URL, no trailing slash)
5. Save
6. Vercel will auto-redeploy (or click "Redeploy")

## Step 6: Test!

1. Visit your frontend URL: `https://your-frontend.vercel.app`
2. Open browser DevTools (F12) → Console
3. Check for errors
4. Test the app functionality

## Verify Backend is Working

Test the health endpoint:
```bash
curl https://YOUR_BACKEND_URL.vercel.app/api/v1/health
```

Should return:
```json
{"success":true,"data":{"status":"ok"}}
```

## Done! 🎉

Your app is now live on Vercel!

---

## Need Help?

- Check `VERCEL_DEPLOYMENT.md` for detailed troubleshooting
- Check Vercel dashboard → Deployments → Logs for errors
- Backend logs: Vercel dashboard → Your Backend Project → Functions → api/index.py → Logs

