import os

SEARCH_KEY = os.environ['SEARCH_KEY']
SEARCH_ID = os.environ['SEARCH_ID']
COUNTRY = "us"

# Key = search key, cx = search id, q = query, start = what page you start on, gl = country
SEARCH_URL = "https://www.googleapis.com/customsearch/v1?key={key}&cx={cx}&q={query}&start={start}&gl=" + COUNTRY

# How many results you want (You only get 100 free links per day)
RESULT_COUNT = 20
