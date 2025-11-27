import chromadb
import os

# 1. Setup the Database
# This creates a folder called 'fin_db' to store your data
client = chromadb.PersistentClient(path="./fin_db") 
collection = client.get_or_create_collection(name="financial_docs")

# 2. Load your text files
files = ["isa_guide.txt", "overdraft_guide.txt", "current_account_debit_card.txt"]
documents = []
ids = []

print("Reading files...")
for file_name in files:
    with open(file_name, "r") as f:
        text = f.read()
        documents.append(text)
        ids.append(file_name)

# 3. Save to the Database
# This automatically turns text into numbers (embeddings) so the AI can search it
collection.add(documents=documents, ids=ids)

print("✅ Knowledge Base Built Successfully! Your data is in the 'fin_db' folder.")
