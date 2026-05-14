import requests
from bs4 import BeautifulSoup
import json
import os

def scrape():
    url = "https://www.shl.com/solutions/products/product-catalog/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    
    print("Scraping SHL catalog...")
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        catalog = []
        
        for link in soup.find_all('a', href=True):
            if '/product-catalog/view/' in link['href'] or '/products/' in link['href']:
                name = link.get_text(strip=True)
                if name and len(name) > 5:
                    full_url = link['href'] if link['href'].startswith('http') else f"https://www.shl.com{link['href']}"
                    catalog.append({"name": name, "url": full_url, "description": f"SHL assessment for {name}"})
        
        # Unique items
        unique_catalog = list({v['url']: v for v in catalog}.values())
        
        os.makedirs('app', exist_ok=True)
        with open('app/catalog.json', 'w', encoding='utf-8') as f:
            json.dump(unique_catalog, f, indent=2)
        print(f"Done! {len(unique_catalog)} items saved.")
    except Exception as e:
        print(f"Scrape failed: {e}")

if __name__ == "__main__":
    scrape()