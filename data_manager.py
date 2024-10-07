import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_path, *args, **kwargs):
        self.db_path = db_path
    
    def setup_database(self, name, **kwargs):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = self.query_generator_log(name, **kwargs)
            cursor.execute(query)
            query = self.query_generator_sold(name, **kwargs)
            cursor.execute(query)
            query = f"CREATE TRIGGER IF NOT EXISTS {name}_sold_trigger AFTER INSERT ON {name} FOR EACH ROW BEGIN DELETE FROM {name}_sold WHERE user_ID = NEW.user_ID; END;"
            cursor.execute(query)
            conn.commit()
        print(f"Table {name} created/checked")
        
    def insert_data(self, name, id, **kwargs):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = f"INSERT INTO {name} ("
                keys = ""
                values = ""
                for key, value in kwargs.items():
                    keys += f"{key}, "
                    values += f"{value}, "
                    
                keys = keys[:-2]
                values = values[:-2]
                query += f"ID, {keys}, timestamp) VALUES ({id} , {values}, '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
                cursor.execute(query)
                conn.commit()
            
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
               print("Eintrag bereits vorhanden")
            else:
                print("Error: ", e)
            
    def read_data(self, name, **kwargs):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row 
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {name}")
            rows = cursor.fetchall()

            dict_rows = [dict(row) for row in rows]

            return dict_rows
        
    def remove_table(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE {name}")
            conn.commit()  
            
    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                cursor.execute(f"DROP TABLE {table[0]}")
            conn.commit()
            
    ###################
    def query_generator_log(self, name, **kwargs):
        query = f"CREATE TABLE IF NOT EXISTS {name} (ID INTEGER PRIMARY KEY"        
        for key, value in kwargs.items():
            query += f", {key} {value}"
        query += ", timestamp TEXT)"
        return query
        
    def query_generator_sold(self, name, **kwargs):
        query = f"CREATE TABLE IF NOT EXISTS {name}_sold (ID INTEGER PRIMARY KEY"        
        for key, value in kwargs.items():
            query += f", {key} {value}"
        query += ", duration TEXT, timestamp TEXT)"
        return query
    
if __name__ == "__main__":
    dbm = DatabaseManager("./data.db")
    dbm.clear_all()