# VoiceForward

## Run Backend
```
cd backend
pip install -r requirements.txt
cp .env.example .env   # add your Featherless API key
uvicorn main:app --reload --port 8000
```

## Run Frontend
```
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
