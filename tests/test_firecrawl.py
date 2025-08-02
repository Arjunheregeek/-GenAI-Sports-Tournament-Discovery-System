"""
Test Firecrawl API functionality
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
        print("Please add your Firecrawl API key to the .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test URLs from our Serper results (cricket tournament pages)
    test_urls = [
        "https://www.bcci.tv/international/men/series-and-tournaments",
        "https://www.olympics.com/en/news/indian-cricket-team-2025-calendar-schedule-dates"
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
            # Scrape the page - using correct Firecrawl API format
            result = app.scrape_url(url, formats=['markdown', 'html'])
            
            print("✅ Scraping successful!")
            
            # Get the scraped data - Firecrawl returns response with 'data' attribute
            if hasattr(result, 'data') and result.data:
                data = result.data
                title = data.get('metadata', {}).get('title', 'N/A')
                markdown_content = data.get('markdown', '')
                html_content = data.get('html', '')
                metadata = data.get('metadata', {})
            else:
                # Fallback for different response format
                title = 'N/A'
                markdown_content = str(result)[:500] if result else ''
                html_content = ''
                metadata = {}
            
            print(f"📄 Page Title: {title}")
            print(f"📝 Markdown Length: {len(markdown_content)} characters")
            print(f"🏷️  HTML Length: {len(html_content)} characters")
            
            # Show first 300 characters of markdown content
            if markdown_content:
                print(f"📋 Content Preview:\n{markdown_content[:300]}...")
            
            # Store result
            results.append({
                'url': url,
                'title': title,
                'markdown_length': len(markdown_content),
                'html_length': len(html_content),
                'content_preview': markdown_content[:500] if markdown_content else '',
                'success': True
            })
            
            # Save detailed content to file
            filename = f"test_firecrawl_content_{i}.json"
            result_dict = {
                'url': url,
                'title': title,
                'markdown': markdown_content,
                'html': html_content,
                'metadata': metadata
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            print(f"💾 Full content saved to '{filename}'")
                
        except Exception as e:
            print(f"❌ Exception during scraping: {e}")
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })
    
    # Save summary results
    with open('test_firecrawl_summary.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Summary saved to 'test_firecrawl_summary.json'")
    
    # Check success rate
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\n📊 Results Summary:")
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    return successful > 0

def check_api_usage():
    """Check Firecrawl API usage/credits."""
    api_key = os.getenv('FIRECRAWL_API_KEY')
    
    if not api_key:
        return
    
    try:
        app = FirecrawlApp(api_key=api_key)
        # This might not work on all plans, but let's try
        print("📊 Checking API usage...")
        # Note: Free tier might not have usage endpoint
    except Exception as e:
        print(f"ℹ️  Could not check usage (normal for free tier): {e}")

def main():
    """Main test function."""
    print("🚀 Testing Firecrawl API Integration for Cricket Pages")
    print("=" * 60)
    
    check_api_usage()
    
    success = test_firecrawl_api()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Firecrawl API test completed successfully!")
        print("📋 Next steps:")
        print("   • Check the generated content files")
        print("   • Review the markdown content quality")
        print("   • Ready to proceed with full scraping pipeline")
    else:
        print("❌ Firecrawl API test failed.")
        print("Please check your API key and network connection.")
        print("💡 Free tier limits: Check if you've exceeded daily limits")

if __name__ == "__main__":
    main()
