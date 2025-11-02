# Vercel Deployment Guide - EU Forecast Hub Backend

## Quick Start

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/euforecast-hub-backend.git
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Configure environment variables (see below)
   - Click "Deploy"

## Environment Variables

Add these in Vercel Dashboard → Project Settings → Environment Variables:

```
DATABASE_URL=postgresql+asyncpg://neondb_owner:YOUR_DATABASE_PASSWORD@ep-icy-rice-ahq4erv1-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
LLAMA_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_API_KEY=your_groq_api_key_here
CORS_ORIGINS=https://your-frontend.vercel.app
APP_NAME=EU ForecastHUB API
API_PREFIX=/api/v1
```

**Important:** 
- Update `CORS_ORIGINS` after deploying the frontend
- Never commit `.env` files or API keys to GitHub

## Project Settings in Vercel

- **Framework Preset:** Other
- **Root Directory:** `./` (default)
- **Build Command:** (leave empty - Vercel auto-detects Python)
- **Output Directory:** (leave empty)
- **Install Command:** `pip install -r requirements.txt`

## API Endpoints

After deployment, your API will be available at:
```
https://your-project.vercel.app/api/v1/health
https://your-project.vercel.app/api/v1/dbn/build
https://your-project.vercel.app/api/v1/dbn/fit
https://your-project.vercel.app/api/v1/dbn/infer
https://your-project.vercel.app/api/v1/builder/run
... etc
```

## Testing

Test your deployment:
```bash
curl https://your-project.vercel.app/api/v1/health
```

Expected response:
```json
{"success":true,"data":{"status":"ok"}}
```

## Function Timeouts

- **Hobby Plan:** 10 seconds max execution time
- **Pro Plan:** 60 seconds max execution time

Note: DBN training operations might timeout on Hobby plan if they take longer than 10 seconds. Consider upgrading to Pro plan or optimizing the training process.

## Troubleshooting

### Build fails
- Check that `requirements.txt` is in the root directory
- Verify Python 3.11 is selected in function settings
- Check build logs in Vercel dashboard

### Database connection errors
- Verify `DATABASE_URL` is correct
- Ensure Neon database allows connections from Vercel's IPs
- Check Vercel function logs for detailed error messages

### API routes return 404
- Verify `vercel.json` routes are configured correctly
- Check that `api/index.py` exists and exports `handler`
- Ensure routes start with `/api/`

### CORS errors
- Update `CORS_ORIGINS` with your frontend URL
- Redeploy backend after updating environment variables
- Check that frontend URL matches exactly (no trailing slashes)

## Updating Deployment

After making code changes:
```bash
git add .
git commit -m "Update code"
git push
```

Vercel will automatically redeploy on every push to your main branch.

