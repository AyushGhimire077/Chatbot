from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from mailLogic import sendMail
import requests
import re

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in environment variables")


class ChatModel(BaseModel):
    message: str


class MailModel(BaseModel): 
    to: str
    subject: str
    body: str    


def check_mail(request: ChatModel):
    mail_patterns = [r"send an? email", r"compose an? email", r"write an? email", r"send mail to", r"email to", r"mail subject", r"email body" ] 
    return any(re.search(pattern, request.message.lower()) for pattern in mail_patterns)


def extract_mail_info(message: str):
    match_subject = re.search(r"subject[:\-]?\s*(.+)", message, re.IGNORECASE)
    match_to = re.search(r"to[:\-]?\s*([\w\.-]+@[\w\.-]+\.\w+)", message, re.IGNORECASE)
    match_body = re.search(r"body[:\-]?\s*(.+)", message, re.IGNORECASE)
    
    subject = match_subject.group(1).strip() if match_subject else None
    to = match_to.group(1).strip() if match_to else None
    body = match_body.group(1).strip() if match_body else None
    
    return subject, to, body


def mail_question_ans(message: str):
    check_question = ["Can you send mail", "Can you compose an email", "Can you write an email", "Can you send mail to", "Can you email to", "Can you mail subject", "Can you email body"]
    
    for question in check_question:
        if re.search(r"\b" + re.escape(question.lower()) + r"\b", message.lower()):
            return True 
        
    return False 

@app.get("/")
async def root():   
    return {"message": "Hellowww"}



@app.post("/chatbot")
async def chatbot(request_data: ChatModel): 
    
    if mail_question_ans(request_data.message):
        return {"message": "Yes I can send mail behalf of you. But you need to provide if mail subject , body and whom to send."}
    
    if check_mail(request_data):
        subject, to, body = extract_mail_info(request_data.message)
        if not subject or not to or not body:
            raise HTTPException(status_code=400, detail="Missing Subject, Recipient, or Body.")

        email_sent = sendMail(to, subject, body)
        return {"message": "Mail sent successfully"} if email_sent else {"message": "Failed to send mail"}

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.9,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": request_data.message}]
            }
        )

        if response.status_code == 200:
            chatbot_message = response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response")
            return {"message": chatbot_message}
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching chatbot response")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)