FinStep UK 🇬🇧: The AI Financial Mentor for Students

💡 The Problem

Young people in the UK often face a "financial cliff edge" when they turn 18. Misunderstanding complex financial products like Overdrafts, ISAs, or Credit Scores can lead to long-term debt.

While students turn to AI for answers, standard chatbots can be dangerous. They may "hallucinate" financial advice (e.g., "You should buy this stock"), which violates FCA (Financial Conduct Authority) regulations and puts users at risk.

🤖 The Solution

FinStep UK is a "Zero-to-Hero" multi-agent AI system designed to bridge this gap. It provides safe, engaging, and compliant financial education.

Instead of a single AI that might make mistakes, we use a Multi-Agent RAG (Retrieval-Augmented Generation) architecture:

The Librarian (The Educator): Retrieves verified facts and explains them in a fun, "cool older sibling" persona.

The Guardian (The Safety Net): A second AI agent that acts as a Compliance Officer, filtering out personal advice and ensuring safety before the user sees the answer.

🏗️ Architecture

The system follows a Sequential Multi-Agent Chain:

graph LR
    User(User Query) -->|Streamlit Interface| Librarian
    
    subgraph "Agent 1: The Librarian"
    Librarian -->|Search Tool| DB[(ChromaDB Vector Store)]
    DB -->|Retrieved Context| Librarian
    Librarian -->|Draft Answer| Draft(Raw Draft)
    end
    
    Draft -->|Review Request| Guardian
    
    subgraph "Agent 2: The Guardian"
    Guardian{Safety Check}
    Guardian -->|Advice Detected| Rewrite[Rewrite to Educational]
    Guardian -->|Safe| Approve[Approve Draft]
    end
    
    Rewrite --> FinalOutput
    Approve --> FinalOutput
    FinalOutput -->|Streamlit Interface| User


✨ Key Features

RAG (Retrieval-Augmented Generation): The AI does not guess; it looks up facts from a verified Knowledge Base (fin_db) containing specific guides on UK financial products.

Role-Playing Persona: The Librarian uses specific prompt engineering to break down complex terms into "The Short Answer," "The Trap ⚠️," and "The Real Cost."

Compliance Guardrails: The Guardian agent enforces a strict "No Advice" policy, rewriting "You should..." suggestions into "Some people choose to..." education.

Session Memory: The agent remembers the context of the chat using Streamlit's session state.

🛠️ Tech Stack

Language: Python 3.10+

LLM: Google Gemini 1.5 Flash (Librarian) & Gemini 1.5 Pro (Guardian)

Database: ChromaDB (Persistent Vector Store)

Frontend: Streamlit

Orchestration: Custom Python Functions

🚀 How to Run Locally

Prerequisites

Python 3.10 or higher installed.

A Google Cloud API Key (Gemini).

Installation Steps

Clone the repository:

git clone [https://github.com/YOUR_USERNAME/FinStep_Capstone.git](https://github.com/YOUR_USERNAME/FinStep_Capstone.git)
cd FinStep_Capstone


Install dependencies:

pip install -r requirements.txt


Set up your API Key:

Create a new folder named .streamlit in the root directory.

Inside it, create a file named secrets.toml.

Add your API key to the file:

GOOGLE_API_KEY = "your_api_key_here"


Build the Knowledge Base:
Run the ingestion script to create the vector database from the text files.

python create_database.py


Run the Application:
Launch the web interface.

streamlit run app.py


☁️ How to Deploy (Streamlit Cloud)

Push your code to GitHub.

Go to Streamlit Community Cloud and connect your repository.

In the app settings, go to Advanced Settings > Secrets.

Paste your API key in the secrets box:

GOOGLE_API_KEY = "your_api_key_here"


Click Deploy.

📂 Project Structure

app.py: The main application containing the Agent logic and Streamlit UI.

create_database.py: Script to ingest text files into ChromaDB.

isa_guide.txt / overdraft_guide.txt: The source data for the Knowledge Base.

.streamlit/secrets.toml: Local file for API keys (ignored by Git).

fin_db/: The generated Vector Database folder (generated locally).

requirements.txt: List of Python dependencies.

📄 License

This project is open-source and available under the MIT License.