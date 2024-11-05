import schedule
import time
import datetime
import json
from db_utils import DatabaseManager
from scraper import WebScraper

def read_json():
    with open ("./traced_objects.json", "r") as file:
        data = json.load(file)
        return data
        
def write_json(data):
    with open ("./traced_objects.json", "w") as file:
        json.dump(data, file)

def scrape_data_and_insert(name:str, webscraper:WebScraper, dbm:DatabaseManager):
    '''
    input: name of the search_object, corresponding WebScraper object, DatabaseManager object
    '''
    
    article_list = webscraper.scrape_links()
    for article in article_list:
        if webscraper.kfz:
            dbm.insert_data(name, article["ID"], article["title"], article["price"], article["user_ID"], article["timestamp"], km=article["km"])
        else:
            dbm.insert_data(name, article["ID"], article["title"], article["price"], article["user_ID"], article["timestamp"])
        
    print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - Data scraped for {name}")

def check_data(tablename:str, webscraper:WebScraper, dbm:DatabaseManager):
    '''
    input: name of the db table, corresponding WebScraper object, DatabaseManager object
    
    reads the data from the database, checks the status of the articles and updates the database.
    If the article is still online, the days_online counter is incremented.
    If the article is offline, the sold status is set to 1.
    '''
    
    articles = dbm.read_data(tablename)
    
    try:
        for article in articles:
            if webscraper.check_article(article):
                dbm.update_data(tablename, article["ID"], 1, 0)
            else:
                days_online = int(datetime.datetime.now() - datetime.datetime.strptime(article["timestamp"], '%Y-%m-%d %H:%M:%S').days)
                dbm.update_data(tablename, article["ID"], 0, days_online)

    except TypeError:
        pass
    
    except Exception as e:
        print(f"wrapper.py: {type(e).__name__} in check_data():\n{e}")
        
def initializing():
    '''
    initializing scrapers, schedules and the database
    
    Returns: 
    scrapers: dictionary with the name of the search_object as key and the WebScraper object as value
    schedules: dictionary with the name of the search_object as key and the checks_per_day as value
    dbm: DatabaseManager object
    '''
    
    search_objects = read_json()
    scrapers = {}
    checks_per_day = {}
    
    dbm = DatabaseManager("./data.db")
    
    # Initializing scrapers and checks_per_day in a dictionary, setting up the database for each search_object
    for search_object in search_objects:
        scrapers[search_object["name"]] = WebScraper(search_object["url"], search_object["blacklist"], bool(search_object["kfz"]))
        checks_per_day[search_object["name"]] = search_object["checks_per_day"]
        dbm.create_table(search_object["name"], kfz=bool(search_object["kfz"]))
        
    return scrapers, checks_per_day, dbm

def update_cycle(name:str, webscraper:WebScraper, dbm:DatabaseManager):
    try:
        check_data(name, webscraper, dbm)
        scrape_data_and_insert(name, webscraper, dbm)
    except Exception as e:
        print(f"wrapper.py: {type(e).__name__} in update_cycle():\n{e}")

def main():
    scrapers, schedules, dbm = initializing()
    for name, scraper in scrapers.items():
        schedule.every(24/schedules[name]).hours.do(update_cycle, name, scraper, dbm)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()