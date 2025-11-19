# Admin UI Deployment Guide

## Prerequisites
- Node.js installed
- Access to the backend API at https://vwe2.sliplane.app

## Setup Instructions

### Option 1: Local Development
1. Navigate to admin-ui directory:
```bash
cd admin-ui
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open http://localhost:3000 in your browser

### Option 2: Deploy to Vercel (Recommended)
1. Push the repository to GitHub
2. Connect the repository to Vercel
3. Set environment variable in Vercel:
   - `REACT_APP_API_URL`: https://vwe2.sliplane.app

### Option 3: Build and Deploy
1. Build the project:
```bash
npm run build
```

2. Deploy the `build` folder to your hosting service

## Features
- **Base Routes Management**: Create and manage API routes
- **Key Pools**: Organize API keys into pools
- **API Keys Management**: Add and monitor API keys
- **User Management**: Create users and set quotas
- **Metrics Dashboard**: View usage statistics
- **Request Logs**: Monitor API requests

## Default Admin Secret Key
The UI is configured to use:
```
change-this-in-production-min-32-chars-required
```

**Important**: Change this in production by setting the ADMIN_SECRET_KEY environment variable in the backend.

## API Endpoints Used
- `/admin/base_routes` - Manage base routes
- `/admin/key_pools` - Manage key pools
- `/admin/key_pools/{id}/keys` - Manage API keys
- `/admin/users` - User management
- `/admin/metrics` - Usage metrics
- `/admin/logs` - Request logs