# EU ForecastHUB — FastAPI Backend

FastAPI backend for EU Forecast Hub, ready for deployment on Vercel.

## Features

- **Forecasts** - Store and manage forecast data
- **Collaborations** - Collaboration management
- **Uploads** - File upload handling
- **Builder** - Kill-chain + LLM-powered forecast generation
- **DBN Endpoints** - Dynamic Bayesian Network model training and inference
  - `/api/v1/dbn/build` - Build model specification
  - `/api/v1/dbn/fit` - Train model with EM algorithm
  - `/api/v1/dbn/infer` - Run forward inference

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/eu_forecasthub
export LLAMA_API_URL=https://api.groq.com/openai/v1/chat/completions
export GROQ_API_KEY=your_key_here
export CORS_ORIGINS=http://localhost:5173

# Run locally
uvicorn api.index:app --reload
```

Visit `http://localhost:8000/api/v1/health`

### Test Deployment Readiness

```bash
python test_deployment.py
```

This will verify:
- All imports work correctly
- FastAPI app can be created
- Vercel handler is properly configured

## Deploy to Vercel

See `DEPLOY_TO_VERCEL.md` for step-by-step instructions.

### Environment Variables Required

Set these in Vercel Dashboard → Project Settings → Environment Variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `LLAMA_API_URL` | Groq API endpoint | `https://api.groq.com/openai/v1/chat/completions` |
| `GROQ_API_KEY` | Groq API key | `gsk_...` |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) | `https://your-frontend.vercel.app` |
| `APP_NAME` | Application name (optional) | `EU ForecastHUB API` |
| `API_PREFIX` | API path prefix (optional) | `/api/v1` |

## API Endpoints

All endpoints are under `/api/v1/`:

- `GET /api/v1/health` - Health check
- `GET /api/v1/forecasts` - List forecasts
- `POST /api/v1/builder/run` - Run forecast builder
- `POST /api/v1/dbn/build` - Build DBN model spec
- `POST /api/v1/dbn/fit` - Train DBN model
- `POST /api/v1/dbn/infer` - Run DBN inference

See API documentation at `/docs` when running locally.

## Project Structure

```
.
├── api/
│   └── index.py          # Vercel serverless function handler
├── app/
│   ├── api/
│   │   └── routes/       # API route handlers
│   ├── core/
│   │   ├── config.py     # Configuration settings
│   │   └── database.py   # Database setup
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   └── services/         # Business logic
│       ├── dbn_engine.py # DBN training/inference engine
│       └── llama_client.py # Groq API integration
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── test_deployment.py   # Deployment verification script
```

## Notes

- File uploads are stored in PostgreSQL (table `uploads`). For production, consider S3-compatible storage.
- Database migrations: `create_all` runs on startup. Add Alembic for production migrations.
- DBN engine uses Noisy-OR with EM algorithm for parameter learning.
- Function timeout on Vercel Hobby plan is 10 seconds. DBN training may timeout if longer.

## License

MIT
