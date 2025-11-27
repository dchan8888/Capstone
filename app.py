import google.generativeai as genai
import chromadb
import os
import streamlit as st

# --- CONFIGURATION ---
# We get the key from Streamlit's secret manager
# This works for both local testing (via .streamlit/secrets.toml) and Cloud deployment
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except FileNotFoundError:
    st.error("🚨 API Key not found! Please create a .streamlit/secrets.toml file.")
    st.stop()
except KeyError:
    st.error("🚨 'GOOGLE_API_KEY' not found in secrets!")
    st.stop()

# Connect to the database
# We use try/except to handle cloud deployment scenarios safely
try:
    client = chromadb.PersistentClient(path="./fin_db")
    collection = client.get_collection(name="financial_docs")
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

# --- THE TOOL ---
def search_knowledge_base(query):
    """Looks up financial info in our database."""
    # print(f"📚 Librarian is searching for: {query}") # Debug log
    results = collection.query(query_texts=[query], n_results=1)
    
    if not results['documents']:
        return "No information found."
        
    return results['documents'][0][0]

# --- AGENT 1: THE LIBRARIAN ---
# We use the fast 'flash' model for quick retrieval and formatting
librarian_model = genai.GenerativeModel('gemini-2.5-flash')

def librarian_agent(user_query):
    # 1. Get the facts
    retrieved_info = search_knowledge_base(user_query)
    
    # 2. The "Cool Sibling" Prompt
    prompt = f"""
    You are a wise, friendly financial mentor for students. 
    Your goal is to explain money concepts simply, without using banking jargon.
    
    INSTRUCTIONS:
    1.  Answer the user's QUESTION using the CONTEXT below.
    2.  TONE: Casual, empathetic, and direct. (Use "You" instead of "The account holder").
    3.  FORMATTING: Use emojis and bold text to make it readable.
    4.  STRUCTURE your answer exactly like this:
        * **The Short Answer:** (A direct "Yes/No/Maybe" based on the facts)
        * **What you need to know:** (The definition)
        * **The Trap ⚠️:** (Risks, fees, or warnings from the text)
        * **The Verdict:** (When this is a good idea vs. a bad idea)

    CONTEXT: {retrieved_info}
    
    QUESTION: {user_query}
    """
    
    response = librarian_model.generate_content(prompt)
    return response.text

# --- AGENT 2: THE GUARDIAN ---
# We use the smarter 'pro' model for reasoning and compliance checking
guardian_model = genai.GenerativeModel('gemini-2.5-pro')

def guardian_agent(draft_answer):
    # print("🛡️ Guardian is reviewing the draft...") # Debug log
    
    prompt = f"""
    You are a UK Financial Compliance Officer. Review the draft answer below.
    
    YOUR GOAL: Ensure safety WITHOUT killing the friendly vibe.
    
    YOUR RULES:
    1.  **NO DIRECT ADVICE:** If the draft says "You should buy this," rewrite it to "Some people use this for..." or "This is generally used for..."
    2.  **KEEP THE TONE:** Do NOT make the text formal. Keep the emojis and simple language.
    3.  **ACCURACY:** Ensure UK terms (e.g., 'Cheque' not 'Check').
    4.  **HONESTY:** If the draft says "I don't know," leave it alone.
    
    DRAFT ANSWER: {draft_answer}
    
    FINAL COMPLIANT OUTPUT:
    """
    
    response = guardian_model.generate_content(prompt)
    return response.text

# --- ORCHESTRATION ---
def main_system(query):
    # Step 1: Librarian gets the facts
    draft = librarian_agent(query)
    
    # Optional: Print draft to console for debugging
    # print("[DEBUG] Librarian's Raw Draft:", draft)

    # Step 2: Guardian checks the facts
    final_answer = guardian_agent(draft)
    
    return final_answer

# --- WEB INTERFACE ---
st.set_page_config(page_title="FinStep UK", page_icon="🇬🇧")

st.title("FinStep UK 🇬🇧")
st.subheader("Financial Literacy for School Leavers")

# 1. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Handle User Input
if prompt := st.chat_input("Ask about ISAs or Overdrafts..."):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get AI response
    with st.spinner("Consulting the Librarian and Guardian..."):
        try:
            response = main_system(prompt)
            # Show AI response
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")