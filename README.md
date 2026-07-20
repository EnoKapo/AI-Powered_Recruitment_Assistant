# 🤖 Boti — AI-Powered Recruitment Assistant

> An internal AI chat assistant, designed to streamline CV evaluation, candidate comparison, and HR document analysis using Google Gemini.

---

## ✨ Features

### 📄 Multi-File CV Upload
Attach one or multiple CVs before sending your message — just like Claude or ChatGPT. Files are staged in a queue, and you type your message and press Enter to send everything together. All files are saved to the session's memory so you can keep referencing them across messages.

### 📊 Give Ratings
One-click scoring of all CVs uploaded in the session using proprietary rubric (max 115 points). No AI inference needed — scores are calculated instantly in Python and displayed in a clean breakdown per candidate.

### 🏆 Explain Winner
After scoring, ask Boti to explain in plain language why the top-ranked candidate stands out — strengths, experience, technical profile, and what differentiates them from the rest.

### 🧠 Access Memory (Per-Session Ground Truth)
Each chat session has its own memory block. Type any facts you want Boti to treat as absolute truth — e.g. _"The role requires 3+ years in finance"_ — and Boti will apply them in every response for that session. Different chats have different memories.

### 💬 Persistent Chat History
All conversations are saved. Switch between past sessions from the sidebar and pick up where you left off, with full message history and file memory restored.

### 📁 Supported File Types
`PDF` · `DOCX` · `TXT` · `MD` · `CSV` · `RTF`

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.14, Django |
| AI Model | Google Gemini 2.5 Flash (`google-genai`) |
| Database | SQLite (local development) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| File Parsing | PyPDF2, python-docx, striprtf |

---

## 📐 BALFIN Scoring Rubric (Max 115 pts)

| Category | Criteria | Points |
|---|---|---|
| **Education** | GPA 2.5 – 4.0 | 30 pts |
| | GPA 1.5 – 2.49 | 10 pts |
| | GPA below 1.5 | 0 pts |
| **Work Experience** | 4+ years | 45 pts |
| | 1 – 3.99 years | 30 pts |
| | 3 – 11 months | 15 pts |
| | Under 3 months | 0 pts |
| **Technical Skills** | Tier A: Python, C#, C++, SQL | 20 pts |
| | Tier B: Java, HTML, CSS, JS, Node.js | 5 pts |
| **Projects** | 3 or more projects | 20 pts |
| | 1 – 2 projects | 10 pts |
| | No projects | 0 pts |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/EnoKapo/AI-Powered_Recruitment_Assistant.git
cd AI-Powered_Recruitment_Assistant
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key
Open `chat/views.py` and replace the `api_key` value with your own key from [Google AI Studio](https://aistudio.google.com/app/apikey).

```python
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the server
```bash
python manage.py runserver
```

Open [http://localhost:8000/chat/](http://localhost:8000/chat/) in your browser.

---

## 📁 Project Structure

```
chatbot/
├── chat/
│   ├── models.py          # ChatSession, ChatMessage, SessionFile, SessionMemory
│   ├── views.py           # All endpoints + AI logic + scoring
│   ├── urls.py            # URL routing
│   ├── manuals/           # .txt knowledge base files loaded into every prompt
│   └── templates/
│       └── chat/
│           └── index.html # Full frontend (single-page)
├── chatbot/
│   └── settings.py
└── manage.py
```

---

## 🔒 Notes

- The Gemini API key is currently hardcoded for development — move it to an environment variable before any production deployment.
- `db.sqlite3` is local only and not included in version control.

---

## 👤 Author

**Eno Kapo** — [github.com/EnoKapo](https://github.com/EnoKapo)
