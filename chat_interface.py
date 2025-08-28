import gradio as gr
from context_chatbot import ImprovedMemoryChatbot

# Create the chatbot instance
chatbot = ImprovedMemoryChatbot("saman_conversations.json")

# Define the chat function for Gradio
def respond(message, history):
    response = chatbot.get_response(message)
    return response

# Create the Gradio interface
demo = gr.ChatInterface(
    fn=respond,
    title="Chat with Saman",
    description="A memory-based chatbot trained on WhatsApp conversations",
    examples=["Aslam alikum", "Kya hal ha?", "Kya kr rhe ho"],
    theme="soft"
)

# Launch the interface
if __name__ == "__main__":
    demo.launch()