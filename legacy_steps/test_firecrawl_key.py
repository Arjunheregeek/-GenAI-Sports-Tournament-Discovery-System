import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('FIRECRAWL_API_KEY')
print(f"Testing Firecrawl API key: {api_key[:10]}...")

# Test API key validity
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Try a simple API call to check if key is valid
test_url = "https://api.firecrawl.dev/v0/scrape"
test_data = {
    "url": "https://example.com"
}

try:
    response = requests.post(test_url, json=test_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 401:
        print("❌ API key is invalid or expired")
        print("💡 Please check your Firecrawl account and get a new API key")
    elif response.status_code == 200:
        print("✅ API key is valid")
    elif response.status_code == 402:
        print("⚠️ API key valid but no credits remaining")
    else:
        print(f"ℹ️ Unexpected status: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error testing API: {e}")
