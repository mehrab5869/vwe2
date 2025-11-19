# Deployment to Sliplane

## Quick Deploy

To deploy this application to Sliplane (https://vwe2.sliplane.app/), follow these steps:

### Option 1: Using Sliplane CLI

1. Install Sliplane CLI:
```bash
npm install -g sliplane
```

2. Login to Sliplane:
```bash
sliplane login
```

3. Deploy:
```bash
sliplane deploy --dockerfile Dockerfile.sliplane
```

### Option 2: Connect Git Repository

1. Push your code to GitHub/GitLab
2. Connect your repository to Sliplane dashboard
3. Set build context to root directory
4. Use `Dockerfile.sliplane` as the Dockerfile path

### Environment Variables

Set these environment variables in Sliplane dashboard:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string  
- `ADMIN_SECRET_KEY`: Secret key for admin authentication (min 32 chars)
- `ENCRYPTION_KEY`: 32-byte encryption key

### Health Check

The application includes a health check endpoint at `/health` that returns:
```json
{"status": "healthy"}
```

### API Endpoints

- `GET /` - Main API endpoint (returns JSON or HTML based on Accept header)
- `GET /health` - Health check
- `/admin/*` - Admin API routes
- `/user/*` - User API routes
- `/proxy/*` - Gateway proxy routes
- `/docs` - API documentation

### Local Development

To run locally:

```bash
# Backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Admin UI (in new terminal)
cd admin-ui
npm install
npm start

# User Dashboard (in new terminal)
cd user-dashboard
npm install
PORT=3001 npm start
```

Services will be available at:
- Backend: http://localhost:8000
- Admin UI: http://localhost:3000
- User Dashboard: http://localhost:3001