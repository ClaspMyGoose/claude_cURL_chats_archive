#!/usr/bin/env python3
"""
API client module
Handles executing cURL commands and returning raw JSON data
"""

import subprocess
import json
import re




def execute_curl_command(curl_args):
    """
    Execute cURL command and return response
    
    Args:
        curl_args (list): Parsed cURL arguments ready for subprocess
        
    Returns:
        dict: Response with 'success', 'data', and 'error' keys
    """
    try:
        print("Executing cURL command...")
        result = subprocess.run(curl_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = f"cURL failed with return code {result.returncode}"
            
            # Check for common issues
            if "403" in result.stderr or "Forbidden" in result.stderr:
                error_msg += "\n❌ Authentication failed (403 Forbidden)"
                error_msg += "\nYour session may have expired. Please get a fresh cURL command."
            elif "404" in result.stderr:
                error_msg += "\n❌ API endpoint not found (404)"
                error_msg += "\nCheck if the URL in your cURL command is correct."
            
            return {
                'success': False,
                'error': error_msg,
                'stderr': result.stderr
            }
        
        # Parse JSON response
        try:
            data = json.loads(result.stdout)
            return {
                'success': True,
                'data': data
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Failed to parse response as JSON: {e}",
                'raw_response': result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"Error executing cURL command: {e}"
        }

def test_curl_command(curl_args):
    """
    Test cURL command with a quick request
    
    Args:
        curl_args (list): Parsed cURL arguments
        
    Returns:
        dict: Test results
    """
    # Modify args for a quick test (limit=1)
    test_args = curl_args.copy()
    
    # Find and modify the URL to limit results
    for i, arg in enumerate(test_args):
        if 'chat_conversations' in arg:
            # Replace or add limit parameter
            if '?' in arg:
                if 'limit=' in arg:
                    # Replace existing limit
                    import re
                    test_args[i] = re.sub(r'limit=\d+', 'limit=1', arg)
                else:
                    # Add limit parameter
                    test_args[i] = arg + '&limit=1'
            else:
                # Add query params
                test_args[i] = arg + '?limit=1'
            break
    
    print("Testing cURL command with limit=1...")
    return execute_curl_command(test_args)

def get_chat_conversations(curl_args, limit=100):
    """
    Get chat conversations with specified limit
    
    Args:
        curl_args (list): Parsed cURL arguments
        limit (int): Number of conversations to fetch
        
    Returns:
        dict: API response
    """
    # Modify args to set the desired limit
    modified_args = curl_args.copy()
    
    # Find and modify the URL to set limit
    for i, arg in enumerate(modified_args):
        if 'chat_conversations' in arg:
            # Replace or add limit parameter
            if '?' in arg:
                if 'limit=' in arg:
                    # Replace existing limit
                    import re
                    modified_args[i] = re.sub(r'limit=\d+', f'limit={limit}', arg)
                else:
                    # Add limit parameter
                    modified_args[i] = arg + f'&limit={limit}'
            else:
                # Add query params
                modified_args[i] = arg + f'?limit={limit}'
            break
    
    return execute_curl_command(modified_args)

def build_messages_curl(chat_uuid, base_curl_file='curl_command.txt'):
    """
    Build cURL command for fetching messages from a specific chat
    Uses the authentication from the base cURL file but changes the endpoint
    """
    try:
        # Read the base cURL command
        with open(base_curl_file, 'r') as f:
            base_curl = f.read().strip()
        
        # Extract organization ID from the base curl
        org_match = re.search(r'/organizations/([a-f0-9-]+)/', base_curl)
        if not org_match:
            raise Exception("Could not find organization ID in base cURL")
        
        org_id = org_match.group(1)
        
        # Build the new URL for messages
        messages_url = f"https://claude.ai/api/organizations/{org_id}/chat_conversations/{chat_uuid}?tree=True&rendering_mode=messages&render_all_tools=true"
        
        # Replace the URL in the base cURL
        # Handle multi-line format
        base_curl = base_curl.replace(' \\\n', ' ').replace('\\\n', ' ')
        
        # Find and replace the URL
        url_pattern = r"curl '([^']+)'"
        new_curl = re.sub(url_pattern, f"curl '{messages_url}'", base_curl)
        
        return new_curl
        
    except Exception as e:
        print(f"Error building messages cURL: {e}")
        return None

def extract_messages(chat_uuid):
    """Extract all messages from a specific chat"""
    
    # Build cURL command for messages
    curl_text = build_messages_curl(chat_uuid)
    if not curl_text:
        return None
    
    # Parse cURL command (same logic as our curl_parser)
    curl_command = curl_text.replace(' \\\n', ' ').replace('\\\n', ' ')
    if curl_command.startswith('curl '):
        curl_command = curl_command[5:]
    
    import shlex
    args = shlex.split(curl_command)
    curl_args = ['curl'] + args
    
    print(f"Fetching messages for chat: {chat_uuid}")
    
    try:
        # Execute cURL command
        result = subprocess.run(curl_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"cURL failed: {result.stderr}")
            return None
        
        # Parse JSON response
        data = json.loads(result.stdout)
        
        return data
        
    except Exception as e:
        print(f"Error extracting messages: {e}")
        return None
