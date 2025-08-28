import json
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
import re
import random

class ImprovedMemoryChatbot:
    def __init__(self, conversation_file, model_name="llama3:8b"):
        """
        Initialize the improved memory-based chatbot
        
        Args:
            conversation_file: Path to the JSON file with conversation data
            model_name: The Ollama model to use
        """
        # Define the persistence directory
        self.persist_directory = "./chroma_db"
        
        # Initialize the embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        
        # Check if the database already exists
        if os.path.exists(self.persist_directory) and os.listdir(self.persist_directory):
            print(f"Loading existing vector database from {self.persist_directory}")
            # Load the existing database
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            # Load conversation data for common phrases and direct matching
            with open(conversation_file, 'r', encoding='utf-8') as f:
                self.conversations = json.load(f)
            
            print(f"Loaded {len(self.conversations)} conversation entries")
            
            # Process just enough for direct matching
            self.contexts = [conv['context'] for conv in self.conversations if conv['response']]
            self.responses = [conv['response'] for conv in self.conversations if conv['response']]
            
            # Extract common phrases 
            self.common_phrases = self.extract_common_phrases()
            print(f"Extracted {len(self.common_phrases.split('- '))-1} common phrases")
            
        else:
            # Database doesn't exist, need to create from scratch
            print(f"Creating new vector database in {self.persist_directory}")
            
            # Load conversation data
            with open(conversation_file, 'r', encoding='utf-8') as f:
                self.conversations = json.load(f)
            
            print(f"Loaded {len(self.conversations)} conversation entries")
            
            # Process the conversation data for retrieval
            self.texts = []
            self.contexts = []
            self.responses = []
            
            # Extract standalone phrases that person uses frequently
            self.common_phrases = self.extract_common_phrases()
            print(f"Extracted {len(self.common_phrases.split('- '))-1} common phrases")
            
            # Create conversation pairs with context
            self.create_conversation_pairs()
            
            # Create and persist vector store
            self.vector_store = Chroma.from_texts(
                texts=self.texts,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            # Save the database
            print("Saving vector database...")
            self.vector_store.persist()
            print("Database saved successfully")
        
        # Initialize the language model
        self.llm = Ollama(model=model_name)
        
        # Define the improved prompt template
        self.prompt = PromptTemplate(
            input_variables=["message", "similar_messages", "common_phrases", "last_message", "name"],
            template="""You are simulating {name}'s texting style based on WhatsApp conversations. Your goal is to respond EXACTLY as {name} would.

Here are messages that {name} has sent in similar contexts:
{similar_messages}

Here are common phrases and expressions that {name} uses:
{common_phrases}

Your last message was: {last_message}

Now, respond to this message as {name} would:
"{message}"

Important guidelines:
1. Use the EXACT same texting style, slang, abbreviations, and emoji usage that {name} uses
2. Match {name}'s typical message length (don't write longer messages than they normally would)
3. Use Roman Urdu exactly as {name} does, with the same spelling patterns
4. Include emojis only if {name} typically uses them
5. Remember to keep the same level of formality/informality

Your response must feel 100% authentic to {name}'s texting style:
"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
        # Create a simple conversation memory - just the last exchange
        self.last_message = ""
        
    def extract_common_phrases(self):
        """Extract common phrases and expressions used by the person"""
        # Get all responses
        all_responses = [conv['response'] for conv in self.conversations if conv['response']]
        
        # Count frequency of short responses (1-5 words)
        phrase_counter = {}
        for response in all_responses:
            # If it's a short response, add to counter
            if len(response.split()) <= 5:
                if response in phrase_counter:
                    phrase_counter[response] += 1
                else:
                    phrase_counter[response] = 1
        
        # Get the most common phrases (appearing at least 5 times)
        common_phrases = [(phrase, count) for phrase, count in phrase_counter.items() if count >= 5]
        common_phrases.sort(key=lambda x: x[1], reverse=True)
        
        # Return the top phrases as a string
        return "\n".join([f"- \"{phrase}\" (used {count} times)" for phrase, count in common_phrases[:30]])
    
    def create_conversation_pairs(self):
        """Process the conversation data to create better pairs for retrieval"""
        for conv in self.conversations:
            if conv['response']:
                text = f"Context: {conv['context']}\nResponse: {conv['response']}"
                self.texts.append(text)
                self.contexts.append(conv['context'])
                self.responses.append(conv['response'])
                
        print(f"Created {len(self.texts)} conversation pairs for retrieval")
    
    def get_response(self, message, name="Saman", num_examples=5):
        """
        Get a response to the given message with improved context matching
        
        Args:
            message: The message to respond to
            name: The name of the person to emulate
            num_examples: Number of examples to use
            
        Returns:
            A response that mimics the style of the person
        """
        # Find similar messages in our database with more examples
        similar_docs = self.vector_store.similarity_search(message, k=num_examples)
        similar_messages = "\n\n".join([doc.page_content for doc in similar_docs])
        
        # Check if we have a direct match (exactly the same or very similar message)
        direct_matches = []
        for i, context in enumerate(self.contexts):
            if context and (message.lower() in context.lower() or context.lower() in message.lower()):
                similarity = len(set(message.lower().split()) & set(context.lower().split())) / max(len(message.split()), len(context.split()))
                if similarity > 0.5:  # If messages are quite similar
                    direct_matches.append(self.responses[i])
        
        # If we have direct matches, randomly select one
        if direct_matches:
            response = random.choice(direct_matches)
        else:
            # Generate a response using the LLM with our improved prompt
            response = self.chain.run(
                message=message,
                similar_messages=similar_messages,
                common_phrases=self.common_phrases,
                last_message=self.last_message,
                name=name
            )
        
        # Update the last message
        self.last_message = response
        
        return response.strip()
        
    def chat(self, name="Saman"):
        """
        Start an interactive chat session
        """
        print(f"Starting chat with {name} (type 'exit' to end)")
        print("-" * 50)
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print(f"{name}: Khuda hafiz!")
                break
                
            response = self.get_response(user_input, name)
            print(f"{name}: {response}")

if __name__ == "__main__":
    # Replace with your actual values
    conversation_file = "saman_conversations.json"
    
    # Create and start the chatbot
    chatbot = ImprovedMemoryChatbot(conversation_file)
    chatbot.chat()