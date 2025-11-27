import google.generativeai as genai
import chromadb
import os
import streamlit as st

# --- CONFIGURATION ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Missing API Key: {e}")
    st.stop()

# --- DATABASE SETUP (Cloud Fix) ---
# This block runs ONLY if the database is missing (like when you first deploy to cloud)
if not os.path.exists("./fin_db"):
    with st.spinner("Building Knowledge Base for the first time..."):
        try:
            # 1. Setup DB
            temp_client = chromadb.PersistentClient(path="./fin_db") 
            temp_collection = temp_client.get_or_create_collection(name="financial_docs")
            
            # 2. Read Files (Make sure these .txt files are in your GitHub repo!)
            files = [
                "isa_guide.txt", 
                "overdraft_guide.txt", 
                "current_account_debit_card.txt"  # <--- NEW FILE ADDED HERE
            ]
            
            documents = []
            ids = []
            
            for file_name in files:
                # We use try-except here just in case a file is missing from the repo
                try:
                    with open(file_name, "r") as f:
                        documents.append(f.read())
                        ids.append(file_name)
                except FileNotFoundError:
                    st.warning(f"Warning: Could not find {file_name}. Skipping.")

            # 3. Add to DB
            if documents:
                temp_collection.add(documents=documents, ids=ids)
                st.success("Database built successfully!")
            else:
                st.error("No documents found to build database.")
                
        except Exception as e:
            st.error(f"Failed to build database: {e}")

# --- CONNECT TO DATABASE ---
try:
    client = chromadb.PersistentClient(path="./fin_db")
    collection = client.get_collection(name="financial_docs")
except Exception as e:
    st.error(f"Error connecting to database: {e}")
    st.stop()

# --- THE TOOL ---
def search_knowledge_base(query):
    """Looks up financial info in our database."""
    results = collection.query(query_texts=[query], n_results=1)
    
    if not results['documents']:
        return "No information found."
        
    return results['documents'][0][0]

# --- AGENT 1: THE LIBRARIAN ---
librarian_model = genai.GenerativeModel('gemini-2.5-flash')

def librarian_agent(user_query):
    retrieved_info = search_knowledge_base(user_query)
    
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
guardian_model = genai.GenerativeModel('gemini-2.5-pro')

def guardian_agent(draft_answer):
    prompt = f"""
    You are a UK Financial Compliance Officer. Review the draft answer below.
    
    YOUR GOAL: Ensure safety WITHOUT killing the friendly vibe.
    
    YOUR RULES:
    1.  **NO DIRECT ADVICE:** If the draft says "You should buy this," rewrite it to "Some people use this for..." or "This is generally used for..."
    2.  **KEEP THE TONE:** Do NOT make the text formal. Keep the emojis and simple language.
    3.  **ACCURACY:** Ensure UK terms (e.g., 'Cheque' not 'Check').
    4.  **HONESTY:** If the draft says "I don't know," leave it alone.
    5.  **NO PREAMBLE:** Output ONLY the final rewritten answer. Do not say "Here is the reviewed version".
    
    DRAFT ANSWER: {draft_answer}
    
    FINAL COMPLIANT OUTPUT:
    """
    
    response = guardian_model.generate_content(prompt)
    return response.text

# --- ORCHESTRATION ---
def main_system(query):
    draft = librarian_agent(query)
    final_answer = guardian_agent(draft)
    return final_answer

# --- WEB INTERFACE ---
st.set_page_config(page_title="FinStep UK", page_icon="🇬🇧")

st.title("FinStep UK 🇬🇧")
st.subheader("Financial Literacy for School Leavers")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about ISAs, Overdrafts, or Student Loans..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Consulting the Librarian and Guardian..."):
        try:
            response = main_system(prompt)
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")