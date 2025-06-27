#!/usr/bin/env python3
"""
Data formatting module
Handles timestamp formatting and data transformation
"""

from datetime import datetime
from zoneinfo import ZoneInfo
import json
from pathlib import Path 
from env import directory_prefix

def format_timestamp(ts_string):
    """
    Convert ISO timestamp to 'YYYY-MM-DD H:MMAM/PM' format in CST
    
    Args:
        ts_string (str): ISO timestamp string
        
    Returns:
        str: Formatted timestamp in CST
    """
    try:
        dt = datetime.fromisoformat(ts_string.replace('Z', '+00:00'))
        cst_dt = dt.astimezone(ZoneInfo('America/Chicago'))
        return cst_dt.strftime('%Y-%m-%d %-I:%M%p')
    except Exception as e:
        print(f"Error formatting timestamp {ts_string}: {e}")
        return ts_string
    
def get_current_CST_timestamp(): 
    """Get current timestamp in CST formatted as 'YYYY-MM-DD H:MMAM/PM'"""
    cst_now = datetime.now(ZoneInfo('America/Chicago'))
    return cst_now.strftime('%Y-%m-%d %-I:%M%p')

def transform_raw_chats(raw_chats):
    """
    Transform raw chat data into cleaned format
    
    Args:
        raw_chats (list): Raw chat data from API
        
    Returns:
        list: Cleaned chat objects
    """
    cleaned_chats = []
    

    most_recent_chat = None 
    most_recent_ts = None 

    for chat in raw_chats:

        try:
            cleaned_chat = {
                'name': chat['name'], 
                'uuid': chat['uuid'],
                'created_at': format_timestamp(chat['created_at']),
                'updated_at': format_timestamp(chat['updated_at']),
                'bucket': format_timestamp(chat['updated_at'])[:10]
            }
            cleaned_chats.append(cleaned_chat)
        except KeyError as e:
            print(f"Warning: Missing key {e} in chat data: {chat}")
            continue
            

        try: 
            
            if most_recent_chat is None or chat['updated_at'] > most_recent_ts:
                most_recent_ts = chat['updated_at']
                most_recent_chat = chat['uuid']
        except Exception as e: 
            print(f'Issue saving most recent conversation: {e}')




    return (most_recent_chat, cleaned_chats)



def parse_conversation(data):
    """Parse the conversation data and extract readable messages"""
    
    if not data:
        return []
    
    messages = []
    messages_key = 'chat_messages'
    
    
    message_data = None

    try:
        message_data = data[messages_key]
    except KeyError as e:
        print(f'Error extracting messages from chat: {e}')

    if not message_data: 
        return []
    
    if isinstance(message_data, list):
        for item in message_data:
            if isinstance(item, dict):
                # Extract message info
                message_info = {
                    'author': item.get('sender', 'unknown'),
                    'msg': parse_message(item.get('content')),
                    'ts': format_timestamp(item.get('created_at'))
                }
                messages.append(message_info)
    
    return messages

def parse_message(message_list):
    # * message comes in as a list containing one obj 
    # we loop to be safe in case it changes in the future
    # is this any safer than just accessing [0] lol? 

    for single_message_obj in message_list:
        return single_message_obj['text']

def save_chats_to_file(current_str_datetime, chats, directory_prefix='../outputs/'):
    """
    Save chat data to JSON file
    
    Args:
        chats (list): Chat data to save
        filename (str): Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """


    filepath = get_output_path(current_str_datetime)

    try:
        with open(filepath, 'w') as f:
            json.dump(chats, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        return False

def print_chat_summary(chats):
    """
    Print a formatted summary of chats
    
    Args:
        chats (list): List of chat objects
    """
    if not chats:
        print("No chats to display")
        return
    
    print(f"\n✅ Found {len(chats)} chats:")
    print("=" * 60)
    
    for i, chat in enumerate(chats, 1):
        print(chat['name'])
        print(chat['uuid'])
        print(chat['msg_list'])
        print(chat['msg_#'])
        print(chat['create_dt'])
        print(chat['update_dt'])
        print(chat['file_name'])
        print()


def get_output_path(current_datetime): 

    home = Path.home()
    path = home / directory_prefix[0] / directory_prefix[1] / directory_prefix[2] / directory_prefix[3]
    filepath = path / f'{current_datetime}_claudeArchive.json'
    return filepath 