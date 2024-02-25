    # Importing Sqlite3 Module
import sqlite3
from typing import List

class Database():
    def __init__(self, database: str) -> None:
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        
    def create_table(self, query: str):
        self.cursor.execute(query)
        self.connection.commit()   
        
    def insert_row(self,query: str):
        self.cursor.execute(query)
        self.connection.commit()   
          
    def get_tables_list(self):
        try:
            # Getting all tables from sqlite_master
            sql_query = """SELECT name FROM sqlite_master 
            WHERE type='table';"""
            # executing our sql query
            self.cursor.execute(sql_query)
            print("List of tables\n")

            # get all tables list
            tables = self.cursor.fetchall()
            # Print the list of tables
            print(tables)
            return tables

        except sqlite3.Error as error:
            print("Failed to execute the above query", error)

    def update_columns_to_null(self, table: str, columns: List[str]):
        for column in columns:
            self.cursor.execute("UPDATE ? SET ? = NULL;",(table,column))
            self.connection.commit()
        
    def copy_table(self, copy_from: str, copy_to: str):
        self.cursor.execute("""
                CREATE TABLE ? AS
                SELECT DISTINCT * FROM ?;
                            """,(copy_to, copy_from))
        self.connection.commit()
        
    def count_images_per_category(self, table: str):
        self.cursor.execute("SELECT image_category,COUNT(image_url) FROM ? GROUP BY image_category",(table,))
        img_count_per_category = self.cursor.fetchall()
        print(img_count_per_category)
        return img_count_per_category
           
    def alter_table_name(self,old_name: str, new_name: str):
        self.cursor.execute("ALTER TABLE ? RENAME TO ?;",(old_name,new_name))
        self.connection.commit()
    
    def delete_table(self, table: str):
        self.cursor.execute("DROP TABLE ?;",(table,))
        self.connection.commit()
    
    def close_connection(self):
        self.connection.close()