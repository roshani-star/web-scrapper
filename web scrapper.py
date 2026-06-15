import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import json
import time
import os
from datetime import datetime
import random
import re

class AdvancedWebScraper:
    def __init__(self):
        self.all_jobs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    
    # Helper: Clean price (remove currency symbols)
    def clean_price(self, price_text):
        """Price ko clean karke float mein convert karo"""
        # Remove currency symbols and convert to float
        clean = re.sub(r'[^\d.]', '', price_text)
        try:
            return float(clean)
        except:
            return 0.0
    
    # Feature 1: Multi-Page Scraping
    def scrape_multiple_pages(self, base_url, pages=5):
        """Multiple pages se data scrape karo"""
        print(f"📥 Scraping {pages} pages...")
        
        for page in range(1, pages + 1):
            url = f"{base_url}catalogue/page-{page}.html"
            print(f"  Page {page}...", end=" ")
            
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code != 200:
                    print(f"❌ Failed")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                books = soup.find_all('article', class_='product_pod')
                
                for book in books:
                    title = book.find('h3').find('a')['title']
                    price_text = book.find('p', class_='price_color').text
                    price = self.clean_price(price_text)  # Fixed: Clean price
                    rating = book.find('p', class_='star-rating')['class'][1]
                    
                    self.all_jobs.append({
                        'title': title,
                        'price': price,
                        'price_original': price_text,  # Original price with symbol
                        'rating': rating,
                        'page': page
                    })
                print(f"✅ {len(books)} items found")
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print(f"\n✅ Total: {len(self.all_jobs)} items scraped!")
        return self.all_jobs
    
    # Feature 2: Search & Filter (Fixed)
    def search_and_filter(self, keyword=None, min_price=None, max_price=None):
        """Scraped data mein search aur filter karo - FIXED"""
        if not self.all_jobs:
            print("⚠️ No data to filter! Run scrape_multiple_pages first.")
            return []
        
        filtered = self.all_jobs.copy()
        
        if keyword:
            filtered = [j for j in filtered if keyword.lower() in j['title'].lower()]
            print(f"🔍 '{keyword}' found: {len(filtered)} items")
        
        if min_price is not None:
            filtered = [j for j in filtered if j['price'] >= min_price]
            print(f"💰 Price >= ${min_price}: {len(filtered)} items")
            
        if max_price is not None:
            filtered = [j for j in filtered if j['price'] <= max_price]
            print(f"💰 Price <= ${max_price}: {len(filtered)} items")
        
        return filtered
    
    # Feature 3: Multiple Export Formats
    def export_data(self, data, filename="scraped_data"):
        """Data ko multiple formats mein save karo"""
        
        if not data:
            print("⚠️ No data to export!")
            return None
        
        # Create exports folder
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV Export
        csv_file = f'exports/{filename}_{timestamp}.csv'
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False)
        print(f"✅ CSV saved: {csv_file}")
        
        # JSON Export
        json_file = f'exports/{filename}_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON saved: {json_file}")
        
        # Excel Export
        try:
            excel_file = f'exports/{filename}_{timestamp}.xlsx'
            df.to_excel(excel_file, index=False)
            print(f"✅ Excel saved: {excel_file}")
        except:
            print("⚠️ Install openpyxl for Excel export: pip install openpyxl")
        
        return csv_file
    
    # Feature 4: Data Statistics (Fixed)
    def show_statistics(self, data):
        """Scraped data ka analysis dikhao"""
        if not data:
            print("⚠️ No data to analyze!")
            return
        
        df = pd.DataFrame(data)
        
        print("\n" + "="*50)
        print("📊 DATA STATISTICS")
        print("="*50)
        print(f"Total Items: {len(data)}")
        print(f"Unique Titles: {df['title'].nunique()}")
        
        if 'price' in df.columns:
            print(f"\n💰 Price Analysis:")
            print(f"  Min Price: ${df['price'].min():.2f}")
            print(f"  Max Price: ${df['price'].max():.2f}")
            print(f"  Avg Price: ${df['price'].mean():.2f}")
        
        if 'rating' in df.columns:
            print(f"\n⭐ Rating Distribution:")
            rating_counts = df['rating'].value_counts()
            for rating, count in rating_counts.items():
                print(f"  {rating}: {count} books")
        
        print("="*50)
    
    # Feature 5: Top N Items
    def get_top_items(self, data, n=10, by='price'):
        """Top N expensive or cheap items"""
        if not data:
            return []
        
        df = pd.DataFrame(data)
        if by == 'price':
            df_sorted = df.sort_values('price', ascending=False)
            print(f"\n🏆 Top {n} Most Expensive Books:")
        elif by == 'price_asc':
            df_sorted = df.sort_values('price', ascending=True)
            print(f"\n🏆 Top {n} Cheapest Books:")
        else:
            return data[:n]
        
        for i, row in df_sorted.head(n).iterrows():
            print(f"  {row['title'][:50]}... - ${row['price']:.2f} ({row['rating']})")
        
        return df_sorted.head(n).to_dict('records')
    
    # Feature 6: Rating Filter
    def filter_by_rating(self, data, min_rating='Three'):
        """Rating ke hisaab se filter karo"""
        ratings_order = ['One', 'Two', 'Three', 'Four', 'Five']
        if min_rating in ratings_order:
            min_index = ratings_order.index(min_rating)
            filtered = [b for b in data if ratings_order.index(b['rating']) >= min_index]
            print(f"⭐ Books with rating >= {min_rating}: {len(filtered)} items")
            return filtered
        return data
    
    # Feature 7: Data Cleaning
    def clean_data(self, data):
        """Data ko clean karo (remove duplicates, empty values)"""
        if not data:
            return []
        
        df = pd.DataFrame(data)
        
        # Remove duplicates
        before = len(df)
        df = df.drop_duplicates(subset=['title'])
        after = len(df)
        print(f"🧹 Removed {before - after} duplicate entries")
        
        # Remove zero price
        before_price = len(df)
        df = df[df['price'] > 0]
        print(f"🧹 Removed {before_price - len(df)} invalid price entries")
        
        return df.to_dict('records')
    
    # Feature 8: Simple Single Page Scrape
    def scrape_single_page(self, url):
        """Single page scrape karo"""
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = []
            books = soup.find_all('article', class_='product_pod')
            for book in books:
                title = book.find('h3').find('a')['title']
                price_text = book.find('p', class_='price_color').text
                price = self.clean_price(price_text)
                rating = book.find('p', class_='star-rating')['class'][1]
                items.append({
                    'title': title, 
                    'price': price,
                    'price_original': price_text,
                    'rating': rating
                })
            return items
        except Exception as e:
            print(f"Error: {e}")
            return []


# ============ MAIN EXECUTION ============

def main():
    print("="*60)
    print("🚀 ADVANCED WEB SCRAPER WITH MULTIPLE FEATURES")
    print("="*60)
    
    # Create scraper object
    scraper = AdvancedWebScraper()
    
    # ===== FEATURE 1: Multi-Page Scraping =====
    print("\n📍 FEATURE 1: Multi-Page Scraping")
    print("-" * 40)
    data = scraper.scrape_multiple_pages("http://books.toscrape.com/", pages=3)
    
    # ===== FEATURE 2: Search & Filter =====
    print("\n📍 FEATURE 2: Search & Filter")
    print("-" * 40)
    python_books = scraper.search_and_filter(keyword="Python")
    cheap_books = scraper.search_and_filter(max_price=30)
    expensive_books = scraper.search_and_filter(min_price=40)
    
    # ===== FEATURE 3: Rating Filter =====
    print("\n📍 FEATURE 3: Rating Filter")
    print("-" * 40)
    high_rated = scraper.filter_by_rating(data, min_rating='Four')
    
    # ===== FEATURE 4: Top Items =====
    print("\n📍 FEATURE 4: Top Books")
    print("-" * 40)
    scraper.get_top_items(data, n=5, by='price')
    scraper.get_top_items(data, n=5, by='price_asc')
    
    # ===== FEATURE 5: Statistics =====
    print("\n📍 FEATURE 5: Data Statistics")
    print("-" * 40)
    scraper.show_statistics(data)
    
    # ===== FEATURE 6: Data Cleaning =====
    print("\n📍 FEATURE 6: Data Cleaning")
    print("-" * 40)
    cleaned_data = scraper.clean_data(data)
    
    # ===== FEATURE 7: Multiple Export Formats =====
    print("\n📍 FEATURE 7: Exporting Data")
    print("-" * 40)
    scraper.export_data(data, "all_books")
    scraper.export_data(python_books, "python_books")
    scraper.export_data(cheap_books, "cheap_books")
    
    # ===== FINAL SUMMARY =====
    print("\n" + "="*60)
    print("🎉 SCRAPING COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"📊 Total items scraped: {len(data)}")
    print(f"🐍 Python books found: {len(python_books)}")
    print(f"💰 Cheap books (under $30): {len(cheap_books)}")
    print(f"⭐ High rated books: {len(high_rated)}")
    print(f"\n📁 Files created in 'exports/' folder")
    print("="*60)


if __name__ == "__main__":
    main()