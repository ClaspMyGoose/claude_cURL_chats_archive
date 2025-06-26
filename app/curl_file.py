#!/usr/bin/env python3
"""
cURL file handling module
Manages reading/writing curl_command.txt and provides help instructions
"""

def read_curl_file(filename='curl_command.txt'):
    """
    Read cURL command from file
    
    Args:
        filename (str): Path to cURL command file
        
    Returns:
        str: cURL command text
        None: if file not found or error
    """
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()
        
        # Check if it's still the sample file
        if 'YOUR_ORG_ID' in content or 'YOUR_COOKIES_HERE' in content:
            print("Please edit curl_command.txt with your actual cURL command.")
            return None
            
        return content
        
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        print_help_instructions()
        return None
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def create_sample_curl_file(filename='curl_command.txt'):
    """
    Create a sample cURL file with instructions
    
    Args:
        filename (str): Path to create sample file
        
    Returns:
        bool: True if successful, False otherwise
    """
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

def print_help_instructions():
    """Print detailed help instructions for getting cURL command"""
    print("\nTo get the cURL command:")
    print("1. Go to https://claude.ai/recents")
    print("2. Open DevTools (F12) > Network tab")
    print("3. Refresh the page")
    print("4. Find the 'chat_conversations' request")
    print("5. Right-click > Copy > Copy as cURL")
    print("6. Paste the command into curl_command.txt")
    print("\nThe cURL command should be multi-line with backslashes like:")
    print("curl 'https://...' \\")
    print("  -H 'header: value' \\")
    print("  -b 'cookies' \\")
    print("  -H 'another: header'")

def check_curl_file_exists(filename='curl_command.txt'):
    """
    Check if cURL file exists and is properly configured
    
    Args:
        filename (str): Path to cURL command file
        
    Returns:
        bool: True if file exists and configured, False otherwise
    """
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()
            
        # Check if it's still the sample file
        if 'YOUR_ORG_ID' in content or 'YOUR_COOKIES_HERE' in content:
            return False
            
        return True
        
    except FileNotFoundError:
        return False