# %%
import sqlite3
import pandas as pd

class DatabaseManager:
    def __init__(self, db_path, *args, **kwargs):
        self.db_path = db_path
    
    def create_table(self, name, kfz=False):
        '''
        Input: name of the table, kfz = True if the table is for vehicles
        Output: None
        
        Creates a table with the given name if it does not exist already
        '''
        
        query = f"CREATE TABLE IF NOT EXISTS {name} (ID INTEGER PRIMARY KEY, title TEXT, price INTEGER, user_ID INTEGER UNIQUE, sold INTEGER, timestamp TEXT, days_online INTEGER)"
        if kfz:
            query = f"CREATE TABLE IF NOT EXISTS {name} (ID INTEGER PRIMARY KEY, title TEXT, price INTEGER, user_ID INTEGER UNIQUE, sold INTEGER, timestamp TEXT, days_online INTEGER, km REAL)"
          
        try:
            with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    print(f"Table {name} created/checked")
        
        except Exception as e:
            print(f"db_utils: {type(e).__name__} occured in create_table() \n {e}") 
                
    def insert_data(self, name, id, title, price, user_id, timestamp, km = None, *args, **kwargs):
        '''
        Input: name of the table, id, title, price, user_id, timestamp, km = None
        Output: None
        
        Inserts the given data into the table unless it exists already.
        If the user_id already exists, the sold value of the old entry is set to 0, (ID, title, price) are updated.
        '''
        
        query = f"INSERT OR IGNORE INTO {name} (ID, title, price, user_ID, sold, timestamp, days_online) VALUES({id}, '{title}', {price}, {user_id}, 0, '{timestamp}', 0) ON CONFLICT (user_ID) DO UPDATE SET ID = excluded.ID, title = excluded.title, price = excluded.price, sold = 0"
        
        if km is not None:
            query = f"INSERT OR IGNORE INTO {name} (ID, title, price, user_ID, sold, timestamp, days_online, km) VALUES({id}, '{title}', {price}, {user_id}, 0, '{timestamp}', 0, {km}) ON CONFLICT (user_ID) DO UPDATE SET ID = excluded.ID, title = excluded.title, price = excluded.price, sold = 0"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                conn.commit()
            
        except Exception as e:
            print(f"db_utils: {type(e).__name__} occured in insert_data() \n {e}") 
            
    def read_data(self, name):
        '''
        input: name of the table
        output: pandas DataFrame
        
        Reads the data from the table with the given name and returns it as a pandas DataFrame
        '''
        
        try:    
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row 
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {name}")
                column_names = [description[0] for description in cursor.description]
                df = pd.DataFrame(cursor.fetchall(), columns=column_names)
                df.set_index("ID", inplace=True)
                
                return df
            
        except Exception as e:
            print(f"db_utils: {type(e).__name__} occured in read_data() \n {e}")
        
    def update_data(self, name, id, sold_status, days_online_increment):
        '''
        input: name of the table, id, sold_status, days_online_increment
        output: None
        
        Updates the sold status and the days online of the entry with the given id
        '''
        
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE {name} SET sold = {sold_status}, days_online = days_online + {days_online_increment} WHERE ID = {id}")
                conn.commit()
                
        except Exception as e:
            print(f"db_utils: {type(e).__name__} occured in update_to_sold() \n {e}")
        
        
    def remove_table(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE {name}")
            conn.commit()  
            
    def clear_all(self):
        tables = self.return_table_names()
        query = "DROP TABLE IF EXISTS " + ", ".join(tables)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            
    def return_table_names(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            return [x[0] for x in tables]
    
if __name__ == "__main__":
    DBM = DatabaseManager("./data.db")
    print(DBM.return_table_names())
    
    print(DBM.read_data("Mario_Kart_Deluxe"))