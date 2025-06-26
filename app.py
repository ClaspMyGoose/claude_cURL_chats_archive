#!/usr/bin/env python3
"""
Main application for Claude chat extraction
Orchestrates all modules to fetch and format chat data
"""

from app import curl_file
from app import curl_parser
from app import api_client
from app import data_formatter

def main():
    """Main application entry point"""
    print("=== Claude Chat Extractor (Modular Version) ===\n")
    
    # Check if cURL file exists and is configured
    if not curl_file.check_curl_file_exists():
        print("No curl_command.txt found or not configured.")
        curl_file.create_sample_curl_file()
        return
    
    # Read cURL command from file
    curl_text = curl_file.read_curl_file()
    if not curl_text:
        return
    
    # Parse cURL command
    curl_args = curl_parser.parse_curl_command(curl_text)
    if not curl_args:
        return
    
    # Validate cURL command
    validation = curl_parser.validate_curl_command(curl_args)
    if not validation['valid']:
        print(f"❌ Invalid cURL command: {validation['error']}")
        curl_file.print_help_instructions()
        return
    
    # Display validation info
    print(f"cURL command validated")
    
    
    # Execute API call
    response = api_client.get_chat_conversations(curl_args, limit=100)
    
    if not response['success']:
        print(f"❌ API call failed: {response['error']}")
        if 'stderr' in response:
            print(f"   Details: {response['stderr']}")
        return
    
    # Transform raw data
    raw_chats = response['data']
    formatted_chats = data_formatter.transform_raw_chats(raw_chats)
    
    
    structured_chats = []

    for chat in formatted_chats: 
        
        chat_obj = {}

        chat_obj['name'] = chat['name']
        chat_obj['uuid'] = chat['uuid']
        # TODO fx calls here 
        chat_obj['msg_list'] = generate_message_list_from_uuid(chat['uuid'])
        # TODO figure out how to hash here 
        chat_obj['msg_#'] = 'Nonsense'
        chat_obj['create_dt'] = chat['created_at']
        chat_obj['update_dt'] = chat['updated_at']
        chat_obj['file_name'] = f'{chat['updated_at']}_{chat['uuid']}_{chat['name']}'

        structured_chats.append(chat_obj)



    # Display results
    data_formatter.print_chat_summary(structured_chats)
    
    # Save to file
    if data_formatter.save_chats_to_file(structured_chats):
        print("Chats saved to claude_chats.json")
    


def generate_message_list_from_uuid(uuid): 

    data = api_client.extract_messages(uuid)

    if not data:
        print(f'No data found in uuid: {uuid}')
        return []

    messages = data_formatter.parse_conversation(data)

    if not messages: 
        print(f'No messages found in data object of uuid: {uuid}. Check objects against logic / keys.')
        return []

    return messages

if __name__ == "__main__":    
    main()