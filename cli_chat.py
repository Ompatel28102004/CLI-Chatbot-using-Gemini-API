import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

load_dotenv()

def initialize_gemini_api():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env or environment variables.")
        print("Please create a .env file with:")
        print("GEMINI_API_KEY=your_api_key_here")
        exit(1)
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash')

def initialize_sentiment_analyzer():
    try:
        nltk.data.find('vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon',quiet=True)
    
    return SentimentIntensityAnalyzer()

def analyze_sentiment(review):
    sentiment_analyzer = initialize_sentiment_analyzer()
    scores = sentiment_analyzer.polarity_scores(review)
    compound = scores['compound']
    
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def save_feedback(feedback):
    with open("feedback.txt", "a") as f:
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Rating: {feedback['rating']}/5\n")
        f.write(f"Review: {feedback['review']}\n")
        f.write(f"Sentiment: {feedback.get('sentiment', 'Unknown')}\n")
        f.write("-" * 50 + "\n")
    
    print("Feedback saved successfully to feedback.txt")

def save_chat_history(user_message, bot_response):
    with open("chat_history.txt", "a") as f:
        f.write(f"User ({time.strftime('%Y-%m-%d %H:%M:%S')}): {user_message}\n")
        f.write(f"Bot: {bot_response}\n\n")

feedback_schema = {
    "name": "collect_feedback",
    "description": "Collect user feedback and rating about the chat experience",
    "parameters": {
        "type": "object",
        "properties": {
            "review": {
                "type": "string",
                "description": "User's review of the chat experience"
            },
            "rating": {
                "type": "integer",
                "description": "User's rating of the chat experience on a scale of 1 to 5"
            }
        },
        "required": ["review", "rating"]
    }
}

def is_exit_intent(model, chat_history):
    system_prompt = """
    You are an exit intent detector. Your only job is to determine if the user's last message 
    indicates they want to end the conversation. Return true ONLY if the user clearly wants to exit 
    (using phrases like "bye", "exit", "end chat", "I want to leave", "goodbye", etc.).
    Return false for all other cases, even if the message seems like a conclusion but doesn't explicitly 
    indicate exit intent.
    """
    
    last_message = chat_history[-1]["parts"][0]
    
    prompt = f"Based on this message, does the user want to exit the conversation? Message: '{last_message}'"

    full_prompt = f"""[Instruction]: {system_prompt}

    [User Message]: {prompt}
    """

    response = model.generate_content(full_prompt)
    response_text = response.text.strip().lower()
    return "true" in response_text or "yes" in response_text

def collect_feedback(model, chat_history):
    system_prompt = """
    The user wants to end the conversation. Politely ask them for a review and rating of their 
    chat experience. Use the collect_feedback function to structure their response.
    """
    
    try:
        combined_prompt = system_prompt + "\n\nPrevious chat:\n" + "\n".join(
            f"{msg['role'].capitalize()}: {msg['parts'][0]}" for msg in chat_history
        )

        response = model.generate_content(
            combined_prompt,
            tools=[{"function_declarations": [feedback_schema]}]
        )

        print(response.text)
        
        feedback_text = input("Your feedback: ")
        
        while True:
            try:
                rating = int(input("Your rating (1-5): "))
                if 1 <= rating <= 5:
                    break
                print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")

        feedback = {
            "review": feedback_text,
            "rating": rating
        }
        
        feedback['sentiment'] = analyze_sentiment(feedback_text)
        
        return feedback
    
    except Exception as e:
        print(f"Error collecting feedback: {str(e)}")
        return None

def main():
    print("Welcome to the Gemini Chat Application!")
    print("Type your messages and press Enter. Type 'exit', 'bye', or similar to end the chat.")
    print("-" * 50)
    
    model = initialize_gemini_api()
    
    chat_history = [{"role": "user", "parts": ["Hello!"]}]
    
    try:
        while True:
            user_message = input("You: ")
            
            chat_history.append({"role": "user", "parts": [user_message]})
            
            if is_exit_intent(model, chat_history):
                feedback = collect_feedback(model, chat_history)
                
                if feedback:
                    save_feedback(feedback)
                
                print("Thank you for chatting! Goodbye!")
                break
            
            prompt = "\n".join(
                f"{msg['role'].capitalize()}: {msg['parts'][0]}"
                for msg in chat_history
            )

            try:
                response = model.generate_content(prompt)
                
                print("Bot:")
                print(response.text)
                
                # Only add to chat history if we got a valid response
                if response and response.text:
                    chat_history.append({"role": "model", "parts": [response.text]})
                    save_chat_history(user_message, response.text)
                else:
                    print("Error: Received empty response from API")
            
            except Exception as e:
                print(f"Error getting response from API: {str(e)}")
                # Remove the user message from history since we couldn't get a response
                chat_history.pop()
    
    except KeyboardInterrupt:
        print("\nChat terminated by user.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()