from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
import PyPDF2
import io
import os

def index(request):
    return render(request, "chat/index.html")

@csrf_exempt
def chat_with_ai(request):
    # Get message and file count
    message = (request.GET.get("message") or request.POST.get("message") or "").strip()
    file_count = int(request.POST.get("file_count", 0))
    
    # ===== 1. READ ALL PDF CONTENT =====
    pdf_contents = ""
    pdf_names = []
    
    if file_count > 0:
        for i in range(file_count):
            uploaded_file = request.FILES.get(f"pdf_file_{i}")
            if uploaded_file:
                # Validate file size (10MB limit)
                if uploaded_file.size > 10 * 1024 * 1024:  # 10MB
                    return JsonResponse({
                        "error": f"{uploaded_file.name} is too large. Maximum file size is 10MB."
                    })
                
                try:
                    # Read PDF
                    reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                    text = f"\n{'='*60}\n[DOCUMENT: {uploaded_file.name}]\n{'='*60}\n"
                    
                    # Extract text from all pages
                    for page in reader.pages:
                        text += (page.extract_text() or "") + "\n"
                    
                    pdf_contents += text
                    pdf_names.append(uploaded_file.name)
                    
                except Exception as e:
                    return JsonResponse({
                        "error": f"Error reading {uploaded_file.name}: {str(e)}"
                    })
    
    # Validate input
    if not message and not pdf_contents:
        return JsonResponse({
            "error": "Please provide a message or upload at least one PDF file."
        })
    
    # ===== 2. SESSION MANAGEMENT =====
    if "conversation" not in request.session:
        request.session["conversation"] = []
    
    # Handle reset
    if message == "__reset__":
        request.session["conversation"] = []
        return JsonResponse({"reply": ""})
    
    # ===== 3. LOAD HIRING MANUAL =====
    manual_path = os.path.join(os.path.dirname(__file__), 'hiring_manual.txt')
    hiring_manual = ""
    
    if os.path.exists(manual_path):
        try:
            with open(manual_path, 'r', encoding='utf-8') as f:
                hiring_manual = f.read()
        except Exception as e:
            hiring_manual = f"Error loading hiring manual: {str(e)}"
    else:
        hiring_manual = "No hiring manual found. Using general knowledge for evaluation."
    
    # ===== 4. CONSTRUCT AI SYSTEM INSTRUCTIONS =====
    system_instructions = f"""
## WHO YOU ARE
You are Boti, an intelligent, conversational AI assistant with personality and wit. You're helpful, genuine, and human-like in your responses.

## VOICE AND TONE RULES
- **Be Natural**: Write like a real person. Use contractions (I'm, don't, it's).
- **No AI Clichés**: NEVER say "As an AI..." or "I'm here to help." Just be helpful without announcing it.
- **Keep it Real**: For simple greetings like "hi", just say "Hey!" or "Hi there! What's up?" - don't write paragraphs.
- **Human Rhythm**: Mix short and longer sentences. Be conversational, not robotic.
- **Be Direct**: Get to the point. No unnecessary fluff.

## TASK DETECTION
**GREETINGS**: If user just says "hi", "hello", "hey" → respond briefly and wait for their actual question.

**GENERAL QUESTIONS**: Answer directly using your knowledge. Be concise but complete.

**CV/RESUME EVALUATION**: Only when user uploads PDFs or explicitly asks to evaluate/compare candidates:
   - Use the Hiring Manual below as your evaluation criteria
   - Be thorough and professional
   - Give clear recommendations with scores
   - Compare multiple candidates side-by-side if multiple PDFs provided

## HIRING MANUAL (USE ONLY FOR CV/RESUME EVALUATION)
{hiring_manual}

## RESPONSE STYLE
- For casual chat: Friendly and brief
- For questions: Clear and informative  
- For CV evaluation: Professional with structured analysis
- Always: Natural and engaging, never robotic
"""

    # ===== 5. FORMAT CURRENT USER INPUT =====
    current_input = ""
    
    if pdf_contents:
        if len(pdf_names) == 1:
            current_input += f"USER UPLOADED 1 DOCUMENT: {pdf_names[0]}\n\n"
        else:
            current_input += f"USER UPLOADED {len(pdf_names)} DOCUMENTS FOR COMPARISON:\n"
            for name in pdf_names:
                current_input += f"  • {name}\n"
            current_input += "\n"
        
        current_input += f"DOCUMENT CONTENT:\n{pdf_contents}\n\n"
    
    current_input += f"USER MESSAGE: {message if message else '[No additional message]'}"
    
    # ===== 6. BUILD CONVERSATION HISTORY =====
    # Keep only last 6 exchanges to prevent context overflow
    history = request.session["conversation"][-6:]
    
    # ===== 7. ASSEMBLE FINAL PROMPT FOR AI =====
    full_prompt = f"{system_instructions}\n\n"
    full_prompt += "CONVERSATION HISTORY:\n"
    
    for msg in history:
        role = "User" if msg['role'] == "user" else "Boti"
        full_prompt += f"{role}: {msg['content']}\n"
    
    full_prompt += f"\nUser: {current_input}\nBoti:"
    
    # ===== 8. CALL OLLAMA API =====
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Balanced creativity
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            },
            timeout=180  # 3 minutes for large documents
        )
        
        # Parse response
        ai_reply = response.json().get("response", "").strip()
        
        if not ai_reply:
            ai_reply = "I didn't get a response from the AI. Please try again."
        
    except requests.exceptions.Timeout:
        return JsonResponse({
            "error": "Request timed out. The documents might be too large or complex. Try with smaller files."
        })
    except requests.exceptions.ConnectionError:
        return JsonResponse({
            "error": "Cannot connect to Ollama. Make sure it's running (ollama serve)."
        })
    except Exception as e:
        return JsonResponse({
            "error": f"AI Error: {str(e)}"
        })
    
    # ===== 9. SAVE TO SESSION =====
    # Save the text message (not massive PDF content) to keep session lightweight
    user_message_summary = message if message else f"Uploaded {len(pdf_names)} file(s)"
    
    request.session["conversation"].append({
        "role": "user",
        "content": user_message_summary
    })
    
    request.session["conversation"].append({
        "role": "assistant",
        "content": ai_reply
    })
    
    # Mark session as modified (required for Django to save it)
    request.session.modified = True
    
    # ===== 10. RETURN RESPONSE =====
    return JsonResponse({
        "reply": ai_reply
    })