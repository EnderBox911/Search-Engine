from bs4 import BeautifulSoup
from urllib.parse import urlparse
from settings import *
import urllib, time

with open("blacklist.txt") as f:
  # Start time
  start_time_list = time.time()
  
  bad_domain_list = set(f.read().split("\n"))
  
  # End time to open list
  end_time_list = time.time()
  list_elapsed = end_time_list - start_time_list
  print("OPEN BLACKLIST FILE:", list_elapsed)


def get_page_content(row):
  # Only get the text from a html
  soup = BeautifulSoup(row["html"], features="html5lib")
  text = soup.get_text()
  return text

def tracker_urls(row):
  overall_time_start = time.time()
  
  #Start time to check for srcs
  start_time_src = time.time()
  
  soup = BeautifulSoup(row["html"], features="html5lib")
  # Finds everything that has the script tag
  scripts = soup.find_all("script", {"src": True})
  srcs = [s.get("src") for s in scripts]
  
  # End time for checking for srcs
  end_time_src = time.time()
  src_elapsed = end_time_src - start_time_src
  print("SRC TIME", src_elapsed)
  
  
  #Start time to check for links
  start_time_lnk = time.time()
  
  # Finds everything that has the link tag
  links = soup.find_all("a", {"href": True})
  href = [l.get("href") for l in links]
  
  # End time for checking for links
  end_time_lnk = time.time()
  lnk_elapsed = end_time_lnk - start_time_lnk
  print("LNK TIME", lnk_elapsed)

  

  # Parses it and leaves just the root domain that the src or link is pointig to
  all_domains = [urlparse(s).hostname for s in srcs + href]

  
  #Start time to check for bad stuff
  start_time_bad = time.time()
  
  bad_domains = [a for a in all_domains if a in bad_domain_list]
  
  # End time for checking for links
  end_time_bad = time.time()
  bad_elapsed = end_time_bad - start_time_bad
  print("BAD TIME", bad_elapsed)
  
  overall_time_end = time.time()
  overall = overall_time_end - overall_time_start
  print("OVERALL", overall)
  
   
  return len(bad_domains)
  

class Filter():
  def __init__(self, results):
    self.filtered = results.copy()

  def content_filter(self):
    # Gets page content for each row of the filtered data frame
    page_content = self.filtered.apply(get_page_content, axis=1)
    word_count = page_content.apply(lambda x: len(x.split(" ")))
    # See if page has more words or less words than the median - Too few is most likely cause they have more ads, photos, etc.
    word_count /= word_count.median()

    # If the webpage has more or half the words as the median webpage fr a given search, then penalize it by pushing it down the ranking
    word_count[word_count <= .5] = RESULT_COUNT
    word_count[word_count != RESULT_COUNT] = 0
    self.filtered["rank"] += word_count

  def tracker_filter(self):
    tracker_count = self.filtered.apply(tracker_urls, axis=1)  
    tracker_count[tracker_count > tracker_count.median()] = RESULT_COUNT * 2
    self.filtered["rank"] += tracker_count

  def filter(self):
    # Resorts the filtered dataframe by ranking
    self.content_filter()
    self.tracker_filter()
    self.filtered = self.filtered.sort_values("rank", ascending=True)
    self.filtered["rank"] = self.filtered["rank"].round()
    return self.filtered
