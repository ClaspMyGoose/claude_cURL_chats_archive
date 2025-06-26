#!/usr/bin/env python3
"""
cURL command parser module
Handles parsing cURL commands into subprocess arguments
"""

import shlex
import re

def parse_curl_command(curl_text):
    """
    Parse cURL command text and convert to subprocess arguments
    
    Args:
        curl_text (str): Raw cURL command text with backslash continuations
        
    Returns:
        list: subprocess arguments ready for execution
        None: if parsing fails
    """
    try:
        # Handle multi-line cURL with backslash continuation
        # Remove backslashes and join lines
        curl_command = curl_text.replace(' \\\n', ' ').replace('\\\n', ' ')
        
        # Remove 'curl' from the beginning if present
        if curl_command.startswith('curl '):
            curl_command = curl_command[5:]
        
        # Use shlex to properly parse the command line
        # This handles quoted arguments correctly
        args = shlex.split(curl_command)
        
        # Add 'curl' back to the beginning
        curl_args = ['curl'] + args
        
        return curl_args
        
    except Exception as e:
        print(f"Error parsing cURL command: {e}")
        print("Make sure the cURL command is properly formatted with backslash continuations")
        return None

def extract_url(curl_args):
    """
    Extract URL from parsed cURL arguments
    
    Args:
        curl_args (list): Parsed cURL arguments
        
    Returns:
        str: The URL or 'Not found'
    """
    if len(curl_args) > 1:
        return curl_args[1]
    return 'Not found'

def extract_org_id(url):
    """
    Extract organization ID from Claude API URL
    
    Args:
        url (str): The API URL
        
    Returns:
        str: Organization ID or None
    """
    org_match = re.search(r'/organizations/([a-f0-9-]+)/', url)
    if org_match:
        return org_match.group(1)
    return None

def validate_curl_command(curl_args):
    """
    Validate that the parsed cURL command looks correct
    
    Args:
        curl_args (list): Parsed cURL arguments
        
    Returns:
        dict: Validation results with url, org_id, and status
    """
    if not curl_args or len(curl_args) < 2:
        return {
            'valid': False,
            'error': 'Invalid cURL command format'
        }
    
    url = extract_url(curl_args)
    org_id = extract_org_id(url)
    
    if 'claude.ai' not in url:
        return {
            'valid': False,
            'error': 'URL does not appear to be a Claude API endpoint'
        }
    
    if not org_id:
        return {
            'valid': False,
            'error': 'Could not extract organization ID from URL'
        }
    
    return {
        'valid': True,
        'url': url,
        'org_id': org_id,
        'arg_count': len(curl_args)
    }