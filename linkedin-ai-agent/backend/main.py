# ✅ Paste everything starting from here
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import io
import time
from random import randint

# Load secrets
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# FastAPI setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# 🚀 LinkedIn Post Generation
# -------------------------------
class PostRequest(BaseModel):
    user_role: str
    industry: str
    topic: str

@app.post("/generate_post/")
def generate_post(data: PostRequest):
    try:
        prompt = f"Create a professional LinkedIn post about {data.topic} in the {data.industry} industry for a person working as {data.user_role}."

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        if response.status_code != 200:
            return {"error": f"Status {response.status_code}: {response.text}"}

        result = response.json()
        return {"post": result['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 📄 Resume Upload & Analysis
# -------------------------------
@app.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        reader = PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        prompt = f"""
        You are a resume parser. Extract the following details from the resume text:
        - Key Skills
        - Total Years of Experience
        - Highest Education Qualification
        Resume Text:
        {text[:3000]}
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        if response.status_code != 200:
            return {"error": f"Status {response.status_code}: {response.text}"}

        result = response.json()
        return {"analysis": result['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 🖊️ Industry Trend Research
# -------------------------------
class IndustryInput(BaseModel):
    industry: str

@app.post("/industry_trends/")
def get_industry_trends(data: IndustryInput):
    try:
        url = f"https://newsapi.org/v2/everything?q={data.industry}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": f"Status {response.status_code}: {response.text}"}
        articles = response.json().get("articles", [])
        headlines = [f"{a['title']} - {a['source']['name']}" for a in articles]
        return {"trends": headlines}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 🧐 Content Strategy Recommendations
# -------------------------------
class StrategyInput(BaseModel):
    user_role: str
    industry: str

@app.post("/content_strategy/")
def content_strategy(data: StrategyInput):
    try:
        prompt = f"""
        You are a LinkedIn content strategist. Suggest 5 types of content a {data.user_role} in the {data.industry} industry should post to grow their personal brand.
        Format each like:
        1. [Content Type] - [Short Description]
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        if response.status_code != 200:
            return {"error": f"Status {response.status_code}: {response.text}"}

        result = response.json()
        return {"strategy": result['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 📊 Performance Analytics (Mock)
# -------------------------------
@app.post("/mock_analytics/")
def mock_analytics():
    try:
        analytics = {
            "views": randint(300, 5000),
            "likes": randint(50, 800),
            "comments": randint(5, 100)
        }
        return {"analytics": analytics}
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# 📝 Advanced Content Generation by Post Type
# -------------------------------
class ContentTypeRequest(BaseModel):
    user_role: str
    industry: str
    topic: str
    post_type: str  # 'article', 'update', or 'carousel'

@app.post("/generate_advanced_content/")
def generate_advanced_content(data: ContentTypeRequest):
    try:
        prompt = f"""
        You are a professional LinkedIn content creator.

        Generate a {data.post_type} for a {data.user_role} in the {data.industry} industry about the topic: \"{data.topic}\".

        Format guidelines:
        - If 'article': Include a title and 3–5 detailed paragraphs.
        - If 'update': Make it short, engaging, and suitable for a quick scroll (2–3 paragraphs).
        - If 'carousel': Include 5–7 slide titles with one-line captions (Slide 1: Title - Caption).
        """

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt.strip()}]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

        if response.status_code != 200:
            return {"error": f"Status {response.status_code}: {response.text}"}

        result = response.json()
        return {"content": result['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}
