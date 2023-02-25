# Helps store data - it is a database
import sqlite3
# Helps read back data base in an easier form
import pandas as pd

# Handle all the interactions with the database
class DBStorage():
  def __init__(self):
    # Data base connection to the db
    self.con = sqlite3.connect("links.db")
    self.setup_tables()

  # Create a table in the data base
  def setup_tables(self):
    # Connection cursor - runs queries against data base
    cur = self.con.cursor()

    # SQL that creates the table 
    # rank = for sorting best links, snippet = small part of webpage to display, created = help sort and create query history, relevance = mark if it is relevant or not (for machine learning to filter and help find what we want), UNIQUE() = makes a constraint so that those values are unique 
    results_table = r"""
      CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY,
        query TEXT,
        rank INTEGER,
        link TEXT,
        title TEXT,
        snippet TEXT,
        html TEXT,
        created DATETIME,
        relevance INTEGER,
        UNIQUE(query, link)
      );
    """

    # Executes the code
    cur.execute(results_table)

    # Commits the changes to the data base
    self.con.commit()

    # Close the cursor connecton
    cur.close()

  # Returns all of the results of a query
  def query_results(self, query):
    # Run a SQL query against data base
    df = pd.read_sql(f"select * from results where query='{query}' order by rank;", self.con)

    return df


  # Insert a row into data base
  def insert_row(self, values):
    # Allows us to query and interact with db
    cur = self.con.cursor()

    try:
      # Values are ?s so that we escape the values properly and are not inserting anything malicious into database
      cur.execute("INSERT INTO results (query, rank, link, title, snippet, html, created) VALUES(?,?,?,?,?,?,?)", values)

      # Write changes to db
      self.con.commit()
      
    except sqlite3.IntegrityError:
      # Data alreadt exists in db
      pass

    # Close connection cursor
    cur.close()
