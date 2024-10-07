import time
import requests
import logging
from bs4 import BeautifulSoup
import re

class WebScraper:
    def __init__(self, url, blacklist=[], kfz=False):
        self.url = url
        self.blacklist = blacklist
        self.kfz = kfz
        self.headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def scrape_mainpage(self):
        article_links = []
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for article in soup.find_all("article"):
                article_links.append(article.find("a")["href"])      
            return article_links
        
        except Exception as e:
            logging.error(f"Fehler beim Scraping: {str(e)}")
        
    def scrape_links(self):
        articles = []
        article_links = self.scrape_mainpage()
        for link in article_links:
            article = {}
            try:
                response = requests.get("https://www.kleinanzeigen.de"+link, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tags = soup.find_all('script')
                
                # Artikel ID
                ID = soup.find("div", id="viewad-ad-id-box").find("ul").find_all("li")[1].text
                article["ID"] = int(ID)
                # Name des Artikels
                title = soup.find("h1").get_text().strip()
                article["title"] = title
                # Preis
                price = self.scrape_price(script_tags)
                if price != 'null':
                    article["price"] = int(price)
                else:
                    continue
                # Preis Typ
                price_type = self.scrape_price_type(script_tags)
                article["price_type"] = price_type
                # Benutzer Link
                user_ID = soup.find("div", id="viewad-profile-box").find("a")["href"].strip().split("=")[-1]
                article["user_ID"] = int(user_ID)
                # Paused
                paused = self.scrape_paused(script_tags)
                article["paused"] = self.string_bool(paused)
                # Deleted
                deleted = self.scrape_deleted(script_tags)
                article["deleted"] = self.string_bool(deleted)
                # Expired
                expired = self.scrape_expired(script_tags)
                article["expired"] = self.string_bool(expired)
                # km-Stand
                if self.kfz:
                    km = self.scrape_milage(soup.find("div", id="viewad-details"))
                    if km != 'null':
                        article["km"] = float(km.split(" ")[0])
                    else:
                        continue
                #blacklist check
                if self.blacklist_check(title):
                    continue
                
            except Exception as e:
                logging.error(f"Fehler beim Scraping: {str(e)}")
                
            articles.append(article)
            time.sleep(2)
        return articles

    def check_article(self, article):
        try:
            response = requests.get("https://www.kleinanzeigen.de/s-anzeige/"+str(article["id"]), headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tags = soup.find_all('script')
            
            actual_status = []
            # Paused
            paused = self.scrape_paused(script_tags)
            actual_status.append(self.string_bool(paused))
            # Deleted
            deleted = self.scrape_deleted(script_tags)
            actual_status.append(self.string_bool(deleted))
            # Expired
            expired = self.scrape_expired(script_tags)
            actual_status.append(self.string_bool(expired))
            
            time.sleep(2)
            if any(actual_status): return True  
            
        except Exception as e:
            logging.error(f"Fehler beim Checking: {str(e)}")
        
                
    def scrape_milage(self, soup):
        li_elements = soup.find_all('li')
        
        for li in li_elements:
            if "Kilometerstand" in li.get_text():
                span = li.find('span')
                if span:
                    return span.get_text().strip()
    
    def scrape_price(self, script_tags):
        for script in script_tags:
            # Check if the script tag has any content
            if script.string:
                # Search for the pattern
                match = re.search(r"adPrice:\s*(\w+)", script.string)
                if match:
                    # Return the captured group (the value inside the quotes)
                    return match.group(1)
                
    def scrape_price_type(self, script_tags):
        for script in script_tags:
            # Check if the script tag has any content
            if script.string:
                # Search for the pattern
                match = re.search(r"adPriceType:\s*'(\w+)'", script.string)
                if match:
                    # Return the captured group (the value inside the quotes)
                    return match.group(1)
    
    def scrape_expired(self, script_tags):
        for script in script_tags:
            # Check if the script tag has any content
            if script.string:
                # Search for the pattern
                match = re.search(r"adExpired:\s*(\w+)", script.string)
                if match:
                    # Return the captured group (the value inside the quotes)
                    return match.group(1)
                
    def scrape_paused(self, script_tags):
        for script in script_tags:
            # Check if the script tag has any content
            if script.string:
                # Search for the pattern
                match = re.search(r"showPausedVeil:\s*(\w+)", script.string)
                if match:
                    # Return the captured group (the value inside the quotes)
                    return match.group(1)
                
    def scrape_deleted(self, script_tags):
        for script in script_tags:
            # Check if the script tag has any content
            if script.string:
                # Search for the pattern
                match = re.search(r"showDeletedVeil:\s*(\w+)", script.string)
                if match:
                    # Return the captured group (the value inside the quotes)
                    return match.group(1)
                
    def blacklist_check(self, title):
        return any(word.lower() in title.lower() for word in self.blacklist)
    
    def string_bool(self, string):
        return string.lower() == "true"
    
if __name__ == "__main__":
    scraper = WebScraper("https://www.kleinanzeigen.de/s-autos/sortierung:preis/c63/k0c216+autos.ez_i:2012%2C2014+autos.power_i:%2C525+autos.schaden_s:nein", ["suche", "t"], True)
    articles = scraper.scrape_links()
    for article in articles:
        print(article)