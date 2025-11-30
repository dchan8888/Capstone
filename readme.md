# 🧢 Cappy: The Savvy Capybara (UK Financial Assistant)

![Status](https://img.shields.io/badge/Status-Live_Prototype-success) ![Track](https://img.shields.io/badge/Track-Agents_For_Good-green) ![Model](https://img.shields.io/badge/Model-Gemini_2.5_Flash-orange) ![Deployment](https://img.shields.io/badge/Deployed-Streamlit_Cloud-FF4B4B)

> **"Lowering your blood pressure while raising your Financial IQ."**

Cappy is an autonomous AI agent designed to help UK school leavers and young adults navigate the confusing world of personal finance. From understanding **ISAs** to avoiding **Overdraft** traps, Cappy provides safe, jargon-free education using a multi-agent architecture.

### 🔗 [Click Here to Try the Live App](https://capstone-fin-assist.streamlit.app/)

---

## 📋 Table of Contents
- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [System Architecture](#-system-architecture)
- [Agent Workflow](#-agent-workflow)
- [Tech Stack](#-tech-stack)
- [Evaluation & Quality](#-evaluation--quality)
- [Installation](#-installation--setup)
- [Video Demo](#-video-demo)

---

## 🚩 The Problem
Financial literacy in the UK is critically low among young adults leaving full-time education.
* **The Knowledge Gap:** Concepts like "Compound Interest," "ISAs," and "Direct Debits" are rarely taught in schools.
* **The "Free Money" Trap:** Students often view overdrafts as free cash rather than debt, leading to long-term credit score damage.
* **The Jargon Barrier:** Traditional banking advice is often dry, overly formal, and intimidating.

## 💡 The Solution
**Cappy** is not just a chatbot; it is a **RAG-augmented Multi-Agent System** that acts as a financial concierge.
1.  **It knows the facts:** It retrieves accurate UK-specific financial data from a curated knowledge base.
2.  **It keeps it chill:** It translates "Bank Speak" into plain English using the "Savvy Capybara" persona.
3.  **It keeps it safe:** A secondary "Guardian" agent reviews every response to ensure compliance and prevent irresponsible financial advice.

---

## 🏗️ System Architecture

Cappy utilizes a **Sequential Chain Pattern** (Librarian -> Guardian) to ensure accuracy and safety.

```mermaid
graph LR
    User(User Input) --> Orchestrator[Main System]
    Orchestrator --> Agent1[Agent 1: The Librarian]
    
    subgraph "Knowledge Retrieval (RAG)"
    Agent1 <--> DB[(ChromaDB\nKnowledge Base)]
    end
    
    Agent1 -->|Draft Response| Agent2[Agent 2: The Guardian]
    
    subgraph "Safety Layer"
    Agent2 -->|Compliance Check| Final[Final Output]
    end
    
    Final --> UI[Streamlit Interface]