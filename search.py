from settings import *
import requests
# For exceptions in requests 
from requests.exceptions import RequestException
import pandas as pd
from storage import DBStorage
# Ensures the query is properly formatted in the url
from urllib.parse import quote_plus
from datetime import datetime

def search_api(query, pages=int(RESULT_COUNT/10)):
  results = []

  for i in range(0,pages):
    # Defines first record of the page
    start = i * 10 + i

    # Makes sures the right values are in the url
    url = SEARCH_URL.format(
      key=SEARCH_KEY,
      cx=SEARCH_ID,
      query=quote_plus(query),
      start=start
    )

    # Makes a request to the custom api
    response = requests.get(url)

    # Response is in json format so need to decode it
    data = response.json()

    # Adds the dictionary to the results
    results += data["items"]

  # Turns list of dictionaries into a dataframe
  res_df = pd.DataFrame.from_dict(results)

  # Adds rank field to dataframe first
  res_df["rank"] = list(range(1, res_df.shape[0] + 1))

  # Filters specific fields and removes extra fields
  res_df = res_df[["link", "rank", "snippet", "title"]]

  return res_df

# Takes a list of links and get thefull html of all of the pages
def scrape_page(links):
  html = []

  for link in links:
    try:
      # Download html of the page
      data = requests.get(link, timeout=5)
      html.append(data.text)
    except RequestException:
      # Can't download the page properly
      html.append("")

  return html


# Runs the search
def search(query):
  # Columns to pass into storage and save fo disk
  columns = ["query", "rank", "link", "title", "snippet", "html", "created"]

  # Initialise storage class
  storage = DBStorage()

  # Checks if query was already run and in database
  stored_results = storage.query_results(query)
  if stored_results.shape[0] > 0:
    # Converting datetime (is a string rn) to a pd datetime object
    stored_results["created"] = pd.to_datetime(stored_results["created"])

    # Makes sure the columns stay in the same order
    return stored_results[columns]

  # Doesn't exist in databasse:
  results = search_api(query)
  
  # Gets the html
  results["html"] = scrape_page(results["link"])
  
  # Removes any results that are empty (from errors in downloading html)
  results = results[results["html"].str.len() > 0].copy()

  results["query"] = query
  results["created"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

  # Remove any extraneous columns and put into right order
  results = results[columns]

  # Insert each row into database
  results.apply(lambda x: storage.insert_row(x), axis=1)

  return results
