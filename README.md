# CLI Chatbot using Gemini API

A command-line chatbot application built with Python and Google's Gemini API.  
It simulates intelligent chat interactions and collects user feedback at the end.

## ✨ Features
- Chat with Gemini LLM in your terminal
- Exit intent detection (e.g., "bye", "exit", "end chat")
- Collects a **review** and **rating** at the end using **Function Calling**
- Saves feedback to `feedback.txt`
- Saves chat history to `chat_history.txt`
- Performs basic sentiment analysis on reviews  

## 🛠 Technologies Used
- Python
- Google Gemini API (Text Generation + Function Calling)
- File I/O for feedback and chat history
- NLTK (for sentiment analysis)

---

## ⚙️ Setup Instructions

1. **Clone the repository** or download the code:

```bash
git clone https://github.com/Ompatel28102004/CLI-Chatbot-using-Gemini-API.git
cd CLI-Chatbot-using-Gemini-API
```

2. **Install the required packages**:

```bash
pip install google-generativeai python-dotenv nltk
```

3. **Setup your environment variables**:

Create a `.env` file in the project root:

```
GEMINI_API_KEY = your_actual_gemini_api_key_here
```

---

## 🚀 How to Run the Application

```bash
python cli_chat.py
```

- Type your messages and press Enter.
- Type **"bye"**, **"exit"**, or **"end chat"** to end the conversation.
- Give your **review and rating** when prompted.

---

## 💬 Example Chat Session

```
Welcome to the Gemini Chat Application!
Type your messages and press Enter. Type 'exit', 'bye', or similar to end the chat.
--------------------------------------------------
You: Hi there!
Bot: 
Hello! How can I assist you today?

You: Tell me a single line joke.
Bot: 
Why don't scientists trust atoms? Because they make up everything!

You: bye
I'm sorry to see you go! Before you leave, could you please provide a rating (1-5) and a quick review of your chat experience today? Your feedback helps me improve!

Please share your thoughts about the chat experience: not baad

On a scale of 1-5, how would you rate your experience?
1: Very Dissatisfied | 2: Dissatisfied | 3: Neutral | 4: Satisfied | 5: Very Satisfied

Your rating (1-5): 4

Processing your feedback...

--------------------------------------------------
FEEDBACK SUMMARY
--------------------------------------------------
Rating: 4/5
Review: Not bad
Sentiment: Neutral

Is this feedback correct? (y/n): y
Feedback saved successfully to feedback.txt
Thank you for your feedback! Review: Not bad, Rating: 4/5
Goodbye!
```

---

## 🔑 Gemini API Setup Guide

- Visit [Google AI Studio](https://aistudio.google.com/app/u/1/apikey?pli=1)
- Sign in with your Google account.
- Go to **"Get API Key"**.
- Copy your key and set it in the `.env` file as:

```
GEMINI_API_KEY=your_api_key_here
```

- Official Docs:
  - [Text Generation](https://ai.google.dev/gemini-api/docs/text-generation)
  - [Function Calling](https://ai.google.dev/gemini-api/docs/function-calling?example=meeting)

---

## 📂 Output Files

- **feedback.txt** — Stores timestamped feedback (review, rating, sentiment)
- **chat_history.txt** — Stores the entire conversation history

---

## 📌 Note
- This project uses **Gemini Flash (2.0)** model for faster and efficient responses.
- Sentiment analysis is implemented using **NLTK VADER** (bonus feature).

---

# ✨ Thank You! ✨
