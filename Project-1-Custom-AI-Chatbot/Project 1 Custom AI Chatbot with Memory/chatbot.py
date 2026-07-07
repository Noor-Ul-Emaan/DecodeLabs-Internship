import os
import google.generativeai as genai
from dotenv import load_dotenv
from utils.chat_memory import ChatMemory

# Load environment variables
load_dotenv()

# --- 1. Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please create .env file with your API key")

# Configure Gemini
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. Initialize Chat Memory ---
# This maintains the in-memory list array for conversation history
chat_memory = ChatMemory()

# --- 3. Main Chat Function ---
def chat_with_bot(user_input):
    """
    Appends user message to history, gets response from AI,
    and appends the response to history.
    """
    # Add user message to history
    chat_memory.add_user_message(user_input)
    
    try:
        # Get the full conversation history
        history = chat_memory.get_history()
        
        # Send entire conversation history to the model
        response = model.generate_content(history)
        bot_reply = response.text
        
        # Add bot response to history
        chat_memory.add_bot_message(bot_reply)
        
        return bot_reply
        
    except Exception as e:
        error_message = f"❌ Error: {e}"
        return error_message

# --- 4. Display Chat History ---
def display_history():
    """Display the entire conversation history"""
    history = chat_memory.get_history()
    print("\n" + "="*50)
    print("📜 CONVERSATION HISTORY")
    print("="*50)
    for msg in history:
        role = msg['role']
        parts = msg['parts'][0]
        if role == 'user':
            print(f"👤 You: {parts}")
        else:
            print(f"🤖 Bot: {parts}")
        print("-"*50)
    print(f"Total messages: {len(history)}")

# --- 5. Terminal User Interface ---
def main():
    print("\n" + "="*60)
    print("🤖  CUSTOM AI CHATBOT WITH MEMORY")
    print("="*60)
    print("📝  This chatbot remembers your entire conversation.")
    print("💡  Commands:")
    print("     - Type your message to chat")
    print("     - Type 'history' to see full conversation")
    print("     - Type 'clear' to clear conversation history")
    print("     - Type 'exit' to end the session")
    print("="*60 + "\n")
    
    while True:
        # Get user input
        user_input = input("👤 You: ").strip()
        
        # Check for commands
        if user_input.lower() == 'exit':
            print("\n👋 Chat session ended. Goodbye!")
            print(f"📊 Total messages exchanged: {len(chat_memory.get_history())}")
            break
            
        elif user_input.lower() == 'history':
            display_history()
            continue
            
        elif user_input.lower() == 'clear':
            chat_memory.clear_history()
            print("🗑️  Conversation history cleared!")
            continue
            
        elif not user_input:
            print("⚠️  Please enter a message.")
            continue
        
        # Get response from bot (updates history automatically)
        print("🤖 Bot: ", end="", flush=True)
        bot_response = chat_with_bot(user_input)
        print(bot_response + "\n")
        
        # Show memory status
        history_count = len(chat_memory.get_history())
        if history_count > 0 and history_count % 5 == 0:
            print(f"💾 [Memory: {history_count} messages stored]")

# --- 6. Run the Application ---
if __name__ == "__main__":
    main()