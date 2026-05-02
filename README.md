# <img src="icons/main icon.png" alt="VoiceForward Icon" width="24" height="24" /> VoiceForward

## Run Backend
```
cd backend
pip install -r requirements.txt
cp .env.example .env   # add your Featherless, Sarvam & MongoDb API key
uvicorn main:app --reload --port 8000
```

## Run Frontend
```
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
