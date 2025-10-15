"""
Test file for Context7 integration - Requests library security patterns
This file demonstrates security issues that Context7 should detect
"""

import requests
from typing import Optional, Dict
import json


# ISSUE 1: SSL verification disabled
# Context7 should flag this as a security risk
def fetch_data_insecure(url: str):
    """Fetch data with SSL verification disabled"""
    response = requests.get(url, verify=False)  # Security risk!
    return response.json()


# ISSUE 2: Basic auth in URL
# Context7 should suggest using HTTPBasicAuth
def fetch_with_basic_auth_url(url: str):
    """Fetch with credentials in URL"""
    # Credentials exposed in URL
    response = requests.get("https://user:password@api.example.com/data")
    return response.json()


# ISSUE 3: Hardcoded credentials
# Context7 should flag hardcoded secrets
def fetch_with_hardcoded_creds():
    """Fetch with hardcoded credentials"""
    response = requests.get(
        "https://api.example.com/data",
        headers={"Authorization": "Bearer hardcoded-token-12345"}  # Security risk!
    )
    return response.json()


# ISSUE 4: No timeout specified
# Context7 should recommend setting timeouts
def fetch_without_timeout(url: str):
    """Fetch without timeout - can hang indefinitely"""
    response = requests.get(url)  # Missing timeout
    return response.json()


# ISSUE 5: Not handling exceptions
# Context7 should suggest proper error handling
def fetch_without_error_handling(url: str):
    """Fetch without error handling"""
    response = requests.get(url, timeout=5)
    # No exception handling - will crash on network errors
    return response.json()


# GOOD PATTERN: Secure request with proper practices
# Context7 should recognize this as correct
def fetch_data_secure(
    url: str,
    api_key: Optional[str] = None,
    timeout: int = 30,
    verify_ssl: bool = True
) -> Dict:
    """
    Fetch data securely with best practices
    
    Args:
        url: API endpoint URL
        api_key: Optional API key from environment/secrets manager
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
    
    Returns:
        Response data as dictionary
    
    Raises:
        requests.exceptions.RequestException: On request failure
    """
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=verify_ssl
        )
        response.raise_for_status()  # Raise exception for 4xx/5xx
        return response.json()
    
    except requests.exceptions.Timeout:
        raise Exception(f"Request to {url} timed out after {timeout}s")
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e.response.status_code}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")


# GOOD PATTERN: Using HTTPBasicAuth
# Context7 should recognize this as recommended pattern
from requests.auth import HTTPBasicAuth
import os


def fetch_with_basic_auth_secure(url: str):
    """Fetch with proper basic authentication"""
    # Credentials from environment, not hardcoded
    username = os.getenv("API_USERNAME")
    password = os.getenv("API_PASSWORD")
    
    response = requests.get(
        url,
        auth=HTTPBasicAuth(username, password),
        timeout=30,
        verify=True
    )
    response.raise_for_status()
    return response.json()


# GOOD PATTERN: Session for multiple requests
# Context7 should recognize this as performance best practice
def fetch_multiple_secure(urls: list):
    """Fetch multiple URLs efficiently with session"""
    results = []
    
    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "KellerAI/1.0",
            "Accept": "application/json"
        })
        
        for url in urls:
            try:
                response = session.get(url, timeout=10, verify=True)
                response.raise_for_status()
                results.append(response.json())
            except requests.exceptions.RequestException as e:
                # Log error but continue processing
                print(f"Failed to fetch {url}: {e}")
                continue
    
    return results


# ISSUE 6: Using deprecated urllib patterns
# Context7 should suggest using requests instead
import urllib.request


def fetch_with_urllib(url: str):
    """Fetch using deprecated urllib (requests is preferred)"""
    response = urllib.request.urlopen(url)  # Older pattern
    return response.read()
