# Vercel Deployment Guide - EU Forecast Hub Frontend

## Quick Start

1. **Push code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/euforecast-hub-frontend.git
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Configure environment variables (see below)
   - Click "Deploy"

## Environment Variables

Add this in Vercel Dashboard → Project Settings → Environment Variables:

```
VITE_API_BASE_URL=https://your-backend.vercel.app/api/v1
```

**Important:** Replace `your-backend.vercel.app` with your actual backend URL from Vercel.

## Project Settings in Vercel

Vercel should auto-detect Vite. If not:

- **Framework Preset:** Vite
- **Root Directory:** `./` (default)
- **Build Command:** `npm run build` (auto-detected)
- **Output Directory:** `dist` (auto-detected)
- **Install Command:** `npm install` (auto-detected)

## Deployment URL

After deployment, your frontend will be available at:
```
https://your-frontend-project.vercel.app
```

## Updating Backend CORS

After deploying the frontend:

1. Go to your **backend** project in Vercel
2. Settings → Environment Variables
3. Edit `CORS_ORIGINS`
4. Add your frontend URL: `https://your-frontend-project.vercel.app`
5. Redeploy backend (or wait for auto-redeploy)

## Testing

1. Visit your frontend URL
2. Open browser DevTools (F12) → Console
3. Check for any errors
4. Test API calls to backend

## Troubleshooting

### Build fails
- Check that `package.json` is in the root directory
- Verify Node.js version (should be 20.x)
- Check build logs in Vercel dashboard
- Try clearing cache: Project Settings → Clear Build Cache

### API calls fail
- Verify `VITE_API_BASE_URL` is set correctly
- Check that backend CORS includes your frontend URL
- Check browser console for CORS errors
- Verify backend is deployed and accessible

### Routes return 404
- This is normal for SPAs - Vercel should rewrite all routes to `index.html`
- Verify `vercel.json` is present and configured correctly
- Check that `dist/index.html` exists after build

### Environment variable not working
- Environment variables starting with `VITE_` are baked into the build
- You need to rebuild after changing `VITE_API_BASE_URL`
- Go to Deployments → Redeploy after updating env vars

## Updating Deployment

After making code changes:
```bash
git add .
git commit -m "Update code"
git push
```

Vercel will automatically redeploy on every push to your main branch.

## Preview Deployments

Vercel automatically creates preview deployments for every branch and pull request. You can:
- Test changes before merging to main
- Share preview URLs with team members
- See preview deployments in Vercel dashboard

