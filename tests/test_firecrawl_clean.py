"""
Test Firecrawl API functionality - Clean Version
Simple test to verify Firecrawl API is working correctly with cricket tournament pages.
"""

import json
import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

# Load environment variables
load_dotenv()

def test_firecrawl_api():
    """Test Firecrawl API with cricket tournament URLs."""
    
    # Get API key from environment
    api_key = os.getenv('FIRECRAWL_API_KEY')
    
    if not api_key or api_key == 'your_firecrawl_api_key_here':
        print("❌ FIRECRAWL_API_KEY not found or not set in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test URLs from our Serper results
    test_urls = [
        "https://www.bcci.tv/international/men/series-and-tournaments"
    ]
    
    # Initialize Firecrawl
    try:
        app = FirecrawlApp(api_key=api_key)
        print("✅ Firecrawl app initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Firecrawl: {e}")
        return False
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🔍 Testing URL {i}/{len(test_urls)}: {url}")
        print("📡 Scraping content with Firecrawl...")
        
        try:
            # Scrape the page
            result = app.scrape_url(url)
            
            if result:
                print("✅ Scraping successful!")
                
                # Extract content using proper attributes
                title = ""
                markdown_content = ""
                
                if hasattr(result, 'metadata') and result.metadata:
                    title = result.metadata.get('title', 'N/A')
                
                if hasattr(result, 'markdown'):
                    markdown_content = result.markdown or ""
                
                print(f"📄 Page Title: {title}")
                print(f"📝 Markdown Length: {len(markdown_content)} characters")
                
                # Show first 300 characters of content
                if markdown_content:
                    print(f"📋 Content Preview:\n{markdown_content[:300]}...")
                else:
                    print("⚠️  No markdown content found")
                
                # Store result
                result_data = {
                    'url': url,
                    'title': title,
                    'markdown_length': len(markdown_content),
                    'content_preview': markdown_content[:500] if markdown_content else '',
                    'success': True
                }
                results.append(result_data)
                
                # Save detailed content
                output_dir = 'test_outputs'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                filename = f"test_firecrawl_content_{i}.json"
                save_data = {
                    'url': url,
                    'title': title,
                    'markdown': markdown_content,
                    'raw_result': str(result)[:1000]  # First 1000 chars of raw result
                }
                
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)
                print(f"💾 Content saved to 'test_outputs/{filename}'")
                
            else:
                print("❌ No result returned")
                results.append({
                    'url': url,
                    'success': False,
                    'error': 'No result returned'
                })
                
        except Exception as e:
            print(f"❌ Exception during scraping: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })
    
    # Save summary
    with open('test_firecrawl_summary.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Results: {successful}/{len(results)} successful")
    
    return successful > 0

def main():
    """Main test function."""
    print("🚀 Testing Firecrawl API for Cricket Pages")
    print("=" * 50)
    
    success = test_firecrawl_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Firecrawl API test successful!")
    else:
        print("❌ Firecrawl API test failed.")
        print("💡 Check your API key and free tier limits")

if __name__ == "__main__":
    main()
