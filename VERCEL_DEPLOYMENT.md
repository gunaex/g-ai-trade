# Deploy Frontend to Vercel

## Prerequisites
- Vercel account (sign up at https://vercel.com)
- Backend deployed on Render (g-ai-trade-backend.onrender.com)

## Step 1: Update API URL

The API URL is already configured in `ui/src/lib/api.ts`:
```typescript
const API_BASE: string = (import.meta as any).env?.VITE_API_URL || 'https://g-ai-trade-backend.onrender.com/api'
```

**For development:** Use Vite proxy (already configured in `vite.config.ts`)
**For production (Vercel):** Uses the hardcoded Render URL above

## Step 2: Build Frontend Locally (Optional Test)

```bash
cd ui
npm install
npm run build
```

This creates a `dist/` folder with production-ready static files.

**Test locally:**
```bash
npm run preview
```

## Step 3: Deploy to Vercel

### Option A: Deploy via Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy from ui folder:**
   ```bash
   cd ui
   vercel
   ```

4. **Follow prompts:**
   - Set up and deploy? `Y`
   - Which scope? Select your account
   - Link to existing project? `N`
   - Project name? `g-ai-trade-frontend` (or your choice)
   - In which directory is your code located? `./`
   - Want to override settings? `N`

5. **Production deployment:**
   ```bash
   vercel --prod
   ```

### Option B: Deploy via Vercel Dashboard

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Configure frontend for Vercel deployment"
   git push origin main
   ```

2. **Import on Vercel:**
   - Go to https://vercel.com/new
   - Import your `g-ai-trade` repository
   - **Framework Preset:** Vite
   - **Root Directory:** `ui`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

3. **Environment Variables (Optional):**
   - Add `VITE_API_URL` if you want to override the default Render URL
   - Value: `https://your-custom-backend.onrender.com/api`

4. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)

## Step 4: Update CORS on Backend

After deploying, add your Vercel URL to the backend CORS whitelist.

**On Render (Backend):**
1. Go to your Render service dashboard
2. Add environment variable:
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-custom-domain.com
   ```
3. Redeploy backend

**Or update in `.env` locally and push:**
```env
ALLOWED_ORIGINS=https://your-app.vercel.app
```

## Step 5: Verify Deployment

1. **Check Vercel URL:**
   - Open your Vercel deployment URL
   - Should see the trading dashboard

2. **Test API connectivity:**
   - Open browser DevTools → Network tab
   - Navigate around the app
   - Check API requests to Render backend succeed (200 OK)

3. **Check CORS:**
   - If you see CORS errors, ensure backend `ALLOWED_ORIGINS` includes your Vercel URL

## Vercel Configuration File (Optional)

Create `ui/vercel.json` for advanced settings:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

## Custom Domain (Optional)

1. Go to Vercel project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Add custom domain to backend `ALLOWED_ORIGINS`

## Environment-Specific API URLs

If you want different API URLs for preview vs production:

**Create `ui/.env.production`:**
```env
VITE_API_URL=https://g-ai-trade-backend.onrender.com/api
```

**Create `ui/.env.development`:**
```env
VITE_API_URL=/api
```

Then update `api.ts`:
```typescript
const API_BASE: string = import.meta.env.VITE_API_URL
```

## Troubleshooting

### Build Fails on Vercel
- Check build logs for missing dependencies
- Ensure `package.json` has all required packages
- Try building locally first: `npm run build`

### API Requests Fail
- Check CORS settings on backend
- Verify `ALLOWED_ORIGINS` includes Vercel URL
- Check Network tab in DevTools for error details

### 404 on Refresh
- Add rewrite rules in `vercel.json` (see above)
- Vercel should auto-detect Vite SPA routing

### TypeScript Errors
- Run `npm run type-check` locally
- Fix any type errors before deploying

## Deployment URLs

- **Backend (Render):** https://g-ai-trade-backend.onrender.com
- **Frontend (Vercel):** https://your-app.vercel.app (after deployment)
- **API Endpoint:** https://g-ai-trade-backend.onrender.com/api

## Quick Deploy Summary

```bash
# 1. Update API URL (already done in api.ts)
# 2. Test build
cd ui
npm install
npm run build
npm run preview

# 3. Deploy to Vercel
vercel --prod

# 4. Update backend CORS
# Add Vercel URL to ALLOWED_ORIGINS on Render

# 5. Access your app
# Open Vercel deployment URL
```

Your full-stack application is now deployed! 🚀
