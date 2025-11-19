# User Dashboard Deployment Guide

## Prerequisites
- Node.js installed
- Access to backend API at https://vwe2.sliplane.app

## Setup Instructions

### Option 1: Local Development
1. Navigate to user-dashboard directory:
```bash
cd user-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm start
```

4. Open http://localhost:3001 in your browser

### Option 2: Deploy to Vercel (Recommended)
1. Push to GitHub repository
2. Connect repository to Vercel
3. Set environment variable in Vercel:
   - `REACT_APP_API_URL`: https://vwe2.sliplane.app

### Option 3: Build and Deploy
1. Build the project:
```bash
npm run build
```

2. Deploy the `build` folder to your hosting service

## Features
- **User Authentication**: Register and login
- **API Key Management**: Create and manage your API keys
- **Usage Dashboard**: Monitor your API usage
- **API Documentation**: Built-in documentation

## How to Use
1. **Register**: Create a new account
2. **Login**: Use your credentials to access the dashboard
3. **Create API Key**: Generate a key for API access
4. **Make Requests**: Use your key in API requests

## API Usage Example
```javascript
const response = await fetch('https://vwe2.sliplane.app/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'gpt-4',
    messages: [{ role: 'user', content: 'Hello!' }]
  })
});
```

## Default Quotas
- Per minute: 10 requests
- Per hour: 100 requests  
- Per day: 1000 requests