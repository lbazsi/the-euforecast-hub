# EU ForecastHUB — Frontend

React + TypeScript frontend for EU Forecast Hub, built with Vite and TailwindCSS.

## Features

- **Builder Page** - Interactive forecast builder with kill-chain stages
- **Forecasts Page** - View and manage forecasts
- **Collaborations Page** - Collaboration features
- **Modern UI** - Built with shadcn/ui components
- **Type-Safe API Client** - Full TypeScript API integration

## Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Set environment variable (create .env file)
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Run development server
npm run dev
```

Visit `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Test Deployment Readiness

```bash
node test_deployment.js
```

Then test the build:

```bash
npm run build
```

If build succeeds without errors, you're ready to deploy!

## Deploy to Vercel

See `VERCEL_DEPLOYMENT.md` for step-by-step instructions.

### Environment Variables Required

Set this in Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `https://your-backend.vercel.app/api/v1` |

**Important:** This must be set before building. Vercel will automatically rebuild when you add environment variables.

## Project Structure

```
.
├── src/
│   ├── components/       # React components
│   │   └── ui/          # shadcn/ui components
│   ├── pages/           # Page components
│   │   ├── Builder.tsx  # Main builder interface
│   │   ├── Forecasts.tsx
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts       # API client
│   │   └── utils.ts     # Utilities
│   └── App.tsx          # Main app component
├── package.json
├── vite.config.ts       # Vite configuration
├── vercel.json          # Vercel configuration
└── test_deployment.js   # Deployment verification script
```

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **shadcn/ui** - UI component library
- **React Router** - Routing
- **TanStack Query** - Data fetching
- **Recharts** - Data visualization

## Development

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Notes

- All API calls go through `src/lib/api.ts` which handles environment variables
- The Builder page is fully integrated with backend endpoints
- CORS must be configured on backend to allow frontend domain

## License

MIT
