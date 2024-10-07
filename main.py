import schedule
import time
import datetime
import json
import data_manager
import scraper

def read_json():
    with open ("./traced_objects.json", "r") as file:
        data = json.load(file)
        return data
        
def write_json(data):
    with open ("./traced_objects.json", "w") as file:
        json.dump(data, file)

def initializing():
    search_objects = read_json()
    search_objects_scraper = {}
    search_objects_schedules = {}
    dbm = data_manager.DatabaseManager("./data.db")

    for search_object in search_objects:
        search_objects_scraper[search_object["name"]] = scraper.WebScraper(search_object["url"], search_object["blacklist"], True)
        search_objects_schedules[search_object["name"]] = search_object["checks_per_day"]
        dbm.setup_database(search_object["name"], title="TEXT", price="INT", price_type="TEXT", user_ID="INT", km="REAL")
        
    return search_objects_scraper, search_objects_schedules, dbm

def scrape_data(name, webscraper, dbm: data_manager.DatabaseManager):
    article_list = webscraper.scrape_links()
    for article in article_list:
        dbm.insert_data(name, article["ID"], title="'"+article["title"]+"'", price=article["price"], price_type="'"+article["price_type"]+"'", user_ID=article["user_ID"], km=article["km"])
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Data scraped for {name}")

def check_data(name, webscraper, dbm: data_manager.DatabaseManager):
    print(dbm.read_data(name+"_sold"))
    articles = dbm.read_data(name)
    for article in articles:
        print(article.keys())
        if webscraper.check_article(article):
            duration = str(datetime.datetime.now() - datetime.datetime.strptime(article["timestamp"], '%Y-%m-%d %H:%M:%S'))
            dbm.insert_data(name+"_sold", article["ID"], title="'"+article["title"]+"'", price=article["price"], price_type="'"+article["price_type"]+"'", user_ID=article["user_ID"], km=article["km"], duration="'"+duration+"'")
            print (f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {article} has not been sold after {duration}")
    print(dbm.read_data(name+"_sold"))

def wrapper(name, webscraper, dbm: data_manager.DatabaseManager):
    try:
        check_data(name, webscraper, dbm)
        scrape_data(name, webscraper, dbm)
    except Exception as e:
        print(f"Error in wrapper(): {e}")

if __name__ == "__main__":
    scrapers, schedules, dbm = initializing()
    for name, scraper in scrapers.items():
        schedule.every(24/schedules[name]).hours.do(wrapper, name, scraper, dbm)
    
    while True:
        schedule.run_pending()
        time.sleep(1)