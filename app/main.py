import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import google.generativeai as genai
from app.models import ChatRequest, ChatResponse
from app.retriever import Retriever

# 1. Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("CRITICAL ERROR: No API Key found in .env file!")
else:
    print(f"API Key loaded. Starts with: {api_key[:5]}...")

genai.configure(api_key=api_key)
app = FastAPI(title="SHL Recommender API")
search_engine = Retriever()
llm = genai.GenerativeModel('gemini-flash-latest')

SYSTEM_PROMPT = """You are an expert SHL Assessment Consultant. 
Your goal is to help recruiters find the right tests for their candidates.
Use the provided context to recommend specific tests. 
If the user is vague, ask for the job role or seniority.
Keep responses professional and concise."""

@app.get("/")
def home():
    return {"status": "online", "message": "SHL API is live", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        user_query = request.messages[-1].content
        
        # Semantic Search
        docs = search_engine.search(user_query)
        context = "\n".join([f"- {d['name']}: {d['url']}" for d in docs])
        
        # AI Generation
        prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser: {user_query}"
        response = llm.generate_content(prompt)
        
        # Grounding: Only include recommendations mentioned by the AI
        final_recs = []
        for d in docs:
            if d['name'].lower() in response.text.lower():
                final_recs.append({"name": d['name'], "url": d['url']})

        return {
            "reply": response.text,
            "recommendations": final_recs[:3],
            "end_of_conversation": False
        }
    except Exception as e:
        # Catching the API key error here
        error_msg = str(e)
        if "API key not valid" in error_msg:
            raise HTTPException(status_code=401, detail="Invalid Google API Key. Check your .env file.")
        raise HTTPException(status_code=500, detail=error_msg)