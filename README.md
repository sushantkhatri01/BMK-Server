# BMK Server

Backend API for BMK - A platform to connect hirers and workers in Nepal.

## Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /users` - Create user
- `GET /users` - List users
- `POST /tasks` - Post a task
- `GET /tasks` - Browse tasks
- `POST /workers` - Register as worker
- `GET /workers` - Browse workers
- `GET /search?q=keyword` - Search tasks and workers
- `GET /stats` - Platform statistics

## Deploy to Render

1. Push this folder to GitHub
2. Go to render.com and sign up
3. Create new Web Service
4. Connect your GitHub repo
5. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn bmk_server:app --host 0.0.0.0 --port $PORT`
