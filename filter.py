from bs4 import BeautifulSoup
from urllib.parse import urlparse
from settings import *
import urllib

def get_page_content(row):
  # Only get the text from a html
  soup = BeautifulSoup(row["html"])
  text = soup.get_text()
  return text


with open("blacklist.txt") as f:
  bad_domain_list = set(f.read().split("\n"))


def tracker_urls(row):
  soup = BeautifulSoup(row["html"])
  # Finds everything that has the script tag
  scripts = soup.find_all("script", {"src": True})
  srcs = [s.get("src") for s in scripts]

  # Finds everything that has the link tag
  links = soup.find_all("a", {"href": True})
  href = [l.get("href") for l in links]

  # Parses it and leaves just the root domain that the src or link is pointig to
  all_domains = [urlparse(s).hostname for s in srcs + href]

  bad_domains = [a for a in all_domains if a in bad_domain_list]
  
  return len(bad_domains)
  

class Filter():
  def __init__(self, results):
    self.filtered = results.copy

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
