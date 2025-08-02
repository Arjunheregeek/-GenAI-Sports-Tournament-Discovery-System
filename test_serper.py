"""
Test Serper API functionality
Simple test to verify Serper API is working correctly.
"""

import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_serper_api():
    """Test Serper API with a simple query."""
    
    # Get API key from environment
    api_key = os.getenv('SERPER_API_KEY')
    
    if not api_key or api_key == 'your_serper_api_key_here':
        print("❌ SERPER_API_KEY not found or not set in .env file")
        print("Please add your Serper API key to the .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test query
    test_query = "Cricket tournament India 2025"
    
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'q': test_query,
        'num': 5,  # Just get 5 results for testing
        'hl': 'en',
        'gl': 'in'
    }
    
    print(f"🔍 Testing with query: '{test_query}'")
    print("📡 Sending request to Serper API...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ API call successful!")
            print(f"📈 Response keys: {list(data.keys())}")
            
            # Check if we have organic results
            if 'organic' in data:
                results = data['organic']
                print(f"🎯 Found {len(results)} organic results")
                
                # Display first few results
                print("\n📋 Sample Results:")
                for i, result in enumerate(results[:3], 1):
                    print(f"\n{i}. Title: {result.get('title', 'N/A')}")
                    print(f"   URL: {result.get('link', 'N/A')}")
                    print(f"   Snippet: {result.get('snippet', 'N/A')[:100]}...")
                
                # Save test results
                with open('test_serper_results.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Full results saved to 'test_serper_results.json'")
                
                return True
            else:
                print("⚠️  No 'organic' results found in response")
                print(f"Available data: {data}")
                return False
                
        elif response.status_code == 401:
            print("❌ Authentication failed - please check your API key")
            return False
        elif response.status_code == 429:
            print("❌ Rate limit exceeded - please wait before trying again")
            return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - please check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Serper API Integration")
    print("=" * 50)
    
    success = test_serper_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Serper API test completed successfully!")
        print("You can now proceed to the next step.")
    else:
        print("❌ Serper API test failed.")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main()
