#!/usr/bin/env python3
"""
Claude chat extractor that reads cURL command from input file
"""

import subprocess
import json
import re
import shlex
from datetime import datetime
from zoneinfo import ZoneInfo

def format_timestamp(ts_string):
    """Convert ISO timestamp to 'YYYY-MM-DD H:MMAM/PM' format in CST"""
    dt = datetime.fromisoformat(ts_string.replace('Z', '+00:00'))
    cst_dt = dt.astimezone(ZoneInfo('America/Chicago'))
    return cst_dt.strftime('%Y-%m-%d %-I:%M%p')

def parse_curl_command(curl_file='curl_command.txt'):
    """Parse cURL command from file and convert to subprocess arguments"""
    try:
        with open(curl_file, 'r') as f:
            curl_command = f.read().strip()
        
        # Handle multi-line cURL with backslash continuation
        # Remove backslashes and join lines
        curl_command = curl_command.replace(' \\\n', ' ').replace('\\\n', ' ')
        
        # Remove 'curl' from the beginning if present
        if curl_command.startswith('curl '):
            curl_command = curl_command[5:]
        
        # Use shlex to properly parse the command line
        # This handles quoted arguments correctly
        args = shlex.split(curl_command)
        
        # Add 'curl' back to the beginning
        curl_args = ['curl'] + args
        
        print(f"Parsed cURL command with {len(curl_args)} arguments")
        
        # Extract and display the URL
        url = curl_args[1] if len(curl_args) > 1 else 'Not found'
        print(f"URL: {url}")
        
        # Extract organization ID from URL for verification
        import re
        org_match = re.search(r'/organizations/([a-f0-9-]+)/', url)
        if org_match:
            org_id = org_match.group(1)
            print(f"Organization ID: {org_id}")
        
        return curl_args
        
    except FileNotFoundError:
        print(f"Error: {curl_file} not found!")
        print("Please create the file and paste your cURL command into it.")
        print("\nTo get the cURL command:")
        print("1. Go to https://claude.ai/recents")
        print("2. Open DevTools (F12) > Network tab")
        print("3. Refresh the page")
        print("4. Find the 'chat_conversations' request")
        print("5. Right-click > Copy > Copy as cURL")
        print(f"6. Paste the command into {curl_file}")
        return None
    except Exception as e:
        print(f"Error parsing cURL command: {e}")
        print("Make sure the cURL command is properly formatted with backslash continuations")
        return None

def get_claude_chats(curl_file='curl_command.txt'):
    """Fetch all Claude chats using cURL command from file"""
    
    # Parse the cURL command from file
    curl_command = parse_curl_command(curl_file)
    if not curl_command:
        return []
    
    try:
        # Execute cURL command
        print("Executing cURL command...")
        result = subprocess.run(curl_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"cURL failed with return code {result.returncode}")
            print(f"Error output: {result.stderr}")
            
            # Check for common issues
            if "403" in result.stderr or "Forbidden" in result.stderr:
                print("\nAuthentication failed (403 Forbidden)")
                print("Your session may have expired. Please get a fresh cURL command.")
            elif "404" in result.stderr:
                print("\nAPI endpoint not found (404)")
                print("Check if the URL in your cURL command is correct.")
            
            return []
            
        # Parse JSON response
        try:
            raw_chats = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"Failed to parse response as JSON: {e}")
            print(f"Response: {result.stdout[:200]}...")
            return []
        
        # Transform into requested format
        cleaned_chats = []
        for chat in raw_chats:
            cleaned_chat = {
                'name': chat['name'], 
                'uuid': chat['uuid'],
                'created_at': chat['created_at'],
                'updated_at': chat['updated_at']
            }
            cleaned_chats.append(cleaned_chat)
        
        return cleaned_chats
        
    except Exception as e:
        print(f"Error fetching chats: {e}")
        return []

def create_sample_curl_file(filename='curl_command.txt'):
    """Create a sample cURL file if one doesn't exist"""
    sample_content = '''curl 'https://claude.ai/api/organizations/YOUR_ORG_ID/chat_conversations?limit=100' \\
  -H 'accept: */*' \\
  -H 'accept-language: en-US,en;q=0.9' \\
  -H 'content-type: application/json' \\
  -b 'YOUR_COOKIES_HERE' \\
  -H 'referer: https://claude.ai/recents' \\
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

# Instructions:
# 1. Go to https://claude.ai/recents  
# 2. Open DevTools (F12) > Network tab
# 3. Refresh the page
# 4. Find the 'chat_conversations' request
# 5. Right-click > Copy > Copy as cURL  
# 6. Replace this entire content with the copied command
# 
# The format should be multi-line with backslashes like:
# curl 'https://...' \\
#   -H 'header: value' \\
#   -b 'cookies' \\
#   -H 'another: header' '''
    
    try:
        with open(filename, 'w') as f:
            f.write(sample_content)
        print(f"Created sample {filename} file.")
        print("Please replace the content with your actual cURL command from DevTools.")
        return True
    except Exception as e:
        print(f"Error creating sample file: {e}")
        return False

def main():
    """Main function"""
    print("=== Claude Chat Extractor (cURL File Version) ===\n")
    
    curl_file = 'curl_command.txt'
    
    # Check if cURL file exists, create sample if not
    try:
        with open(curl_file, 'r') as f:
            content = f.read().strip()
            
        # Check if it's still the sample file
        if 'YOUR_ORG_ID' in content or 'YOUR_COOKIES_HERE' in content:
            print("Please edit curl_command.txt with your actual cURL command.")
            return
            
    except FileNotFoundError:
        print("No curl_command.txt found. Creating sample file...")
        create_sample_curl_file(curl_file)
        return
    
    # Fetch chats
    chats = get_claude_chats(curl_file)
    
    if chats:
        print(f"\nFound {len(chats)} chats:")
        print("=" * 60)
        
        for i, chat in enumerate(chats, 1):
            print(f"{i:2d}. {chat['name']}")
            print(f"     UUID: {chat['uuid']}")
            print(f"     Created: {format_timestamp(chat['created_at'])}")
            print(f"     Updated: {format_timestamp(chat['updated_at'])}")
            print()
        
        # Save to file
        with open('claude_chats.json', 'w') as f:
            json.dump(chats, f, indent=2)
        
        print(f"Chats saved to claude_chats.json")
        
    else:
        print("No chats found or error occurred")
        print("\nTroubleshooting:")
        print("1. Make sure you're logged into Claude")
        print("2. Get a fresh cURL command from DevTools")
        print("3. Update curl_command.txt with the new command")

if __name__ == "__main__":
    main()