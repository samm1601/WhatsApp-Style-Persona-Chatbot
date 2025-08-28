import json

def parse_whatsapp_chat(file_path, person_of_interest):
    """
    Parse a WhatsApp chat export to extract messages from a specific person using a line-by-line approach.
    
    Args:
        file_path: Path to the WhatsApp chat export file
        person_of_interest: Name of the person whose messages we want
        
    Returns:
        A list of dictionaries containing the person's messages and context
    """
    # Read the file line by line
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Process lines
    conversations = []
    last_message = None
    last_sender = None
    
    print(f"Total lines in file: {len(lines)}")
    
    message_count = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try to split by the first occurrence of " - "
        try:
            timestamp, rest = line.split(" - ", 1)
            # Now split by the first colon to separate sender and message
            sender, message = rest.split(": ", 1)
            
            message_count += 1
            
            # Skip media messages
            if '<Media omitted>' in message:
                continue
                
            # Skip system messages
            if ": " not in rest:
                continue
                
            if person_of_interest in sender:
                # If there was a previous message from someone else, create a conversation pair
                if last_message and person_of_interest not in last_sender:
                    conversations.append({
                        'context': last_message,
                        'response': message,
                        'timestamp': timestamp
                    })
                # Otherwise, just save as a standalone message
                else:
                    conversations.append({
                        'context': '',
                        'response': message,
                        'timestamp': timestamp
                    })
            
            last_message = message
            last_sender = sender
            
            # Print some progress information
            if message_count % 1000 == 0:
                print(f"Processed {message_count} messages...")
                
        except ValueError:
            # This line doesn't match our expected format, could be a continuation of a previous message
            continue
    
    print(f"Successfully processed {message_count} messages")
    return conversations

def save_conversations(conversations, output_file):
    """Save parsed conversations to a JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(conversations)} conversation pairs to {output_file}")
    if conversations:
        print(f"Sample conversation pairs:")
        for conv in conversations[:3]:
            print(f"Context: {conv['context']}")
            print(f"Response: {conv['response']}")
            print("---")
    else:
        print("No conversations were extracted!")

# Example usage
if __name__ == "__main__":
    # Replace these with your actual values
    file_path = "D:\Projects\Customized ChatBot\WhatsApp Chat with Saman\WhatsApp Chat with Saman.txt"
    person_of_interest = "Saman"
    output_file = "saman_conversations.json"
    
    try:
        conversations = parse_whatsapp_chat(file_path, person_of_interest)
        save_conversations(conversations, output_file)
        
        # Print some statistics
        print(f"Total messages from {person_of_interest}: {len(conversations)}")
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()