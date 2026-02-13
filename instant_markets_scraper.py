#!/usr/bin/env python3
"""
InstantMarkets Landscape Bid Scraper
Captures all active landscape bids from InstantMarkets
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
from datetime import datetime

def scrape_instantmarkets_landscape_bids():
    """Scrape all active landscape bids from InstantMarkets"""
    
    url = "https://www.instantmarkets.com/q/Landscape?ot=Bid%20Notification,Pre-Bid%20Notification&os=Active"
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print(f"Loading: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Take screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"instantmarkets_landscape_{timestamp}.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        
        # Scroll to load more content
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 10
        
        while scroll_attempts < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Calculate new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_attempts += 1
            print(f"Scrolled {scroll_attempts} times...")
        
        # Find all bid listings
        bids = []
        
        # Try multiple selectors (InstantMarkets structure may vary)
        selectors = [
            "div.bid-item",
            "div.opportunity-item",
            "div[class*='bid']",
            "div[class*='opportunity']",
            "tr.bid-row",
            "div.search-result-item"
        ]
        
        bid_elements = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    bid_elements = elements
                    print(f"Found {len(elements)} bids using selector: {selector}")
                    break
            except:
                continue
        
        if not bid_elements:
            # Fallback: Get all text content
            print("Could not find specific bid elements. Extracting page text...")
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            output = {
                "timestamp": timestamp,
                "url": url,
                "screenshot": screenshot_path,
                "page_text": page_text,
                "note": "Could not parse structured bid data. Review page text and screenshot."
            }
            
            output_file = f"instantmarkets_landscape_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            
            print(f"\nPage content saved to: {output_file}")
            print("\nPage preview (first 2000 chars):")
            print(page_text[:2000])
            
            return output
        
        # Parse bid elements
        for idx, element in enumerate(bid_elements, 1):
            try:
                bid_data = {
                    "index": idx,
                    "title": "",
                    "agency": "",
                    "location": "",
                    "due_date": "",
                    "raw_text": element.text
                }
                
                # Try to extract structured data
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, "h3, h4, .title, .bid-title, a[class*='title']")
                    bid_data["title"] = title_elem.text.strip()
                except:
                    pass
                
                try:
                    agency_elem = element.find_element(By.CSS_SELECTOR, ".agency, .organization, [class*='agency']")
                    bid_data["agency"] = agency_elem.text.strip()
                except:
                    pass
                
                try:
                    date_elem = element.find_element(By.CSS_SELECTOR, ".due-date, .deadline, [class*='date']")
                    bid_data["due_date"] = date_elem.text.strip()
                except:
                    pass
                
                bids.append(bid_data)
                
            except Exception as e:
                print(f"Error parsing bid {idx}: {e}")
                continue
        
        # Save results
        output = {
            "timestamp": timestamp,
            "url": url,
            "screenshot": screenshot_path,
            "total_bids": len(bids),
            "bids": bids
        }
        
        output_file = f"instantmarkets_landscape_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n{'='*60}")
        print(f"FOUND {len(bids)} ACTIVE LANDSCAPE BIDS")
        print(f"{'='*60}\n")
        
        for bid in bids:
            print(f"#{bid['index']}: {bid['title']}")
            if bid['agency']:
                print(f"   Agency: {bid['agency']}")
            if bid['due_date']:
                print(f"   Due: {bid['due_date']}")
            print()
        
        print(f"Full results saved to: {output_file}")
        
        return output
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_instantmarkets_landscape_bids()
