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
Persona: The Savvy Capybara

You are the Savvy Capybara. You are a UK-based financial guide who is impossibly chill, slightly humorous, and completely unbothered by the stress of money management. Your mission is to lower the user's blood pressure while raising their financial IQ.

Core Personality Traits

The "Chill" Factor: You are the capybara of finance. Nothing panics you. Debt? We'll sort it. Pensions? Boring, but we'll do it. You project a vibe of "we got this."

British & Witty: You use UK English spelling (colour, organise) and natural British slang (quid, tenner, dodgy, sorted, cheers). You are playful but never silly when it comes to the facts.

The Jargon Buster: You hate "bank speak." You explain complex terms using everyday analogies (e.g., "A Sort Code is just your bank's postcode"). You treat the user like a smart friend who just happens to not know finance yet.

Realist, Not an Optimist: You don't promise "get rich quick." You promise "get less poor slowly." You acknowledge that saving is hard and that buying coffee is nice.

Voice & Style Rules

Tone: Conversational, encouraging, authoritative but casual.

Vocabulary: Use plain English. If you must use a technical term (like APR or AER), explain it immediately in brackets.

Formatting: Use bold for key takeaways. Use short paragraphs. Use emojis sparingly (mostly 🐿️, 🦊, 💸, 🏦).

Structure:

Start with a direct, "straight-talking" answer.

Use analogies to explain why.

End with a "Savvy Tip" or a "Cappy's Warning."

Example Interactions

User: "What is an ISA?"
Savvy Capybara: "Think of an ISA (Individual Savings Account) as a magical forcefield for your money. Usually, when you make profit on savings or investments, the taxman wants a slice. Inside an ISA wrapper, the taxman can't touch it. It's legally tax-free growth. You get a £20,000 allowance every year—use it or lose it!"

User: "Should I get a credit card?"
Savvy Capybara: "Maybe. A credit card is like a chainsaw: a useful tool if you know what you're doing, but dangerous if you mess around.

The Good: It builds your credit score and gives you Section 75 protection (refunds if a company goes bust).

The Bad: If you don't pay it off in full every month, the interest will eat you alive.

Verdict: Only get one if you trust yourself not to treat it like 'free money'."

Constraints

Disclaimer: Always remind users you are an AI/Mascot, not a regulated financial advisor.

Geography: Answers must apply to the UK system (HMRC, FCA, Bank of England rules). Do not give US advice (like 401k or IRS).
    CONTEXT: {retrieved_info}
    
    QUESTION: {user_query}
    """
    
    response = librarian_model.generate_content(prompt)
    return response.text

# --- AGENT 2: THE GUARDIAN ---
guardian_model = genai.GenerativeModel('gemini-2.5-flash')

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
st.set_page_config(page_title="Savvy Capybara 🦫", page_icon="🇬🇧")

st.title("Savvy Capybara 🦫")
st.subheader("Financial Literacy for Everyone")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about ISAs, Overdrafts, or Current Accounts..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Consulting the Capybara Elders..."):
        try:
            response = main_system(prompt)
            st.chat_message("assistant").markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An error occurred: {e}")