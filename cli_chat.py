import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

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

def analyze_sentiment_with_gemini(model, review):
    system_prompt = """
    You are a sentiment analysis assistant. Given a user review, classify the sentiment as:
    - Positive
    - Neutral
    - Negative
    
    Be concise. Return only one of the three words above.
    """

    prompt = f"{system_prompt}\n\nReview: {review}"

    try:
        response = model.generate_content(prompt)
        sentiment = response.text.strip().capitalize()
        if sentiment in {"Positive", "Neutral", "Negative"}:
            return sentiment
        else:
            return "Unknown"
    except Exception as e:
        print(f"Error during Gemini sentiment analysis: {str(e)}")
        return "Unknown"

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

    while True:
        user_review = input("\nPlease share your thoughts about the chat experience: ")
        if len(user_review.strip()) == 0:
            print("Review cannot be empty. Please provide some feedback.")
            continue
            
        validation_prompt = """
        You are a review validator. Check if the user's review is valid feedback about a chat experience.
        Return ONLY "valid" or "invalid" based on whether this seems like legitimate feedback.
        """
        
        try:
            validation_response = model.generate_content(f"{validation_prompt}\n\nReview: {user_review}")
            validation_result = validation_response.text.strip().lower()
            
            if "invalid" in validation_result:
                print("Please provide meaningful feedback about your chat experience.")
                continue
            break
        except Exception:
            break
    
    print("\nOn a scale of 1-5, how would you rate your experience?")
    print("1: Very Dissatisfied | 2: Dissatisfied | 3: Neutral | 4: Satisfied | 5: Very Satisfied")
    
    while True:
        user_rating = input("\nYour rating (1-5): ")
        try:
            rating = int(user_rating)
            if 1 <= rating <= 5:
                break
            else:
                print(f"Invalid input: {user_rating}. Please enter a number between 1 and 5.")
        except ValueError:
            print(f"Invalid input: {user_rating}. Please enter a number between 1 and 5.")
    
    print("\nProcessing your feedback...")
    
    try:
        system_prompt = """
        You are a feedback processor for a chat application. The user has provided a review and rating.
        
        Your tasks:
        1. Clean up the review text (fix typos, grammar, etc.)
        2. Extract the key points of feedback
        3. Structure the feedback appropriately
        4. Return the processed feedback by calling the collect_feedback function
        
        Respond ONLY by calling the collect_feedback function with the processed feedback.
        """
        
        prompt = f"{system_prompt}\n\nOriginal Review: {user_review}\nRating: {rating}/5"
        
        try:
            response = model.generate_content(
                prompt,
                tools=[{"function_declarations": [feedback_schema]}]
            )
            
            feedback = None
            candidate = response.candidates[0]
            
            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        func_call = part.function_call
                        args = dict(func_call.args)
                        
                        processed_review = args.get("review", user_review)
                        if not processed_review or len(processed_review.strip()) < 3:
                            processed_review = user_review
                            
                        processed_rating = args.get("rating", rating)
                        if not isinstance(processed_rating, int) or not (1 <= processed_rating <= 5):
                            processed_rating = rating
                        
                        sentiment = analyze_sentiment_with_gemini(model, processed_review)
                        
                        feedback = {
                            "review": processed_review,
                            "rating": processed_rating,
                            "sentiment": sentiment
                        }
            
            if not feedback:
                print("Using original feedback with sentiment analysis...")
                sentiment = analyze_sentiment_with_gemini(model, user_review)
                feedback = {
                    "review": user_review,
                    "rating": rating,
                    "sentiment": sentiment
                }
                
        except Exception as e:
            print(f"Error using Gemini for feedback processing: {str(e)}")
            print("Processing feedback locally...")
            
            sentiment = analyze_sentiment_with_gemini(model, user_review)
            feedback = {
                "review": user_review,
                "rating": rating,
                "sentiment": sentiment
            }
        
        print("\n" + "-" * 50)
        print("FEEDBACK SUMMARY")
        print("-" * 50)
        print(f"Rating: {feedback['rating']}/5")
        print(f"Review: {feedback['review']}")
        print(f"Sentiment: {feedback['sentiment']}")
        
        confirm = input("\nIs this feedback correct? (y/n): ").lower()
        if confirm != 'y' and confirm != 'yes':
            print("Let's try again.")
            return collect_feedback(model, chat_history)
            
        return feedback
        
    except Exception as e:
        print(f"Error during feedback collection: {str(e)}")
        
        return {
            "review": user_review,
            "rating": rating,
            "sentiment": "Unknown"
        }
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
                print(f"Thank you for your feedback! Review: {feedback['review']}, Rating: {feedback['rating']}/5")
                print("Goodbye!")
                break
                        
            
            prompt = "\n".join(
                f"{msg['role'].capitalize()}: {msg['parts'][0]}"
                for msg in chat_history
            )

            try:
                response = model.generate_content(prompt)
                
                print("Bot:")
                print(response.text)
                
                if response and response.text:
                    chat_history.append({"role": "model", "parts": [response.text]})
                    save_chat_history(user_message, response.text)
                else:
                    print("Error: Received empty response from API")
            
            except Exception as e:
                print(f"Error getting response from API: {str(e)}")
                chat_history.pop()
    
    except KeyboardInterrupt:
        print("\nChat terminated by user.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()