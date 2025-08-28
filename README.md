# WhatsApp-Style Persona Chatbot
![Chatbot UI](https://via.placeholder.com/800x400.png?text=Project+Screenshot)


This repository contains a chatbot designed to emulate a specific texting style, trained on past conversation data. The chatbot learns how a person typically writes — including tone, slang, message length, and Roman Urdu patterns — and then generates new replies in that style.  

It uses **LangChain**, a **Chroma vector database**, and a **local LLM via Ollama** to generate personalized responses. The system retrieves semantically similar past message–response pairs, builds a prompt with those examples plus frequent short phrases, and then generates a reply that feels natural and contextually aligned.  

Two interfaces are included:
1. **Console Chat Loop** — for quick local testing.
2. **Gradio Web UI** — a shareable chat interface in the browser.

---

## ✨ Features
- Mimics conversational tone and texting patterns based on your dataset.
- Retrieval-augmented generation: finds the most relevant past examples before responding.
- Supports Roman Urdu and short-form texting styles.
- Lightweight memory for maintaining conversational flow.
- Works fully offline with a local LLM (via [Ollama](https://ollama.ai/)).
- Easy to run either from the terminal or a web browser.

---
