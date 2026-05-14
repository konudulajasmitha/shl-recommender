import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Required for the front-end to connect
from dotenv import load_dotenv
import google.generativeai as genai
from app.models import ChatRequest, ChatResponse
from app.retriever import Retriever

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

app = FastAPI(title="SHL Recommender API")

# --- CORS FIX START ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your local index.html to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- CORS FIX END ---

search_engine = Retriever()
llm = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = """You are an expert SHL Consultant. 
Use the context to recommend assessments. Ask clarifying questions if the role is vague. 
Keep it professional and concise."""

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        user_query = request.messages[-1].content
        docs = search_engine.search(user_query)
        context = "\n".join([f"- {d['name']}: {d['url']}" for d in docs])
        
        prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser: {user_query}"
        response = llm.generate_content(prompt)
        
        # Grounding logic
        final_recs = [{"name": d['name'], "url": d['url']} for d in docs if d['name'].lower() in response.text.lower()]

        return {"reply": response.text, "recommendations": final_recs[:3], "end_of_conversation": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))