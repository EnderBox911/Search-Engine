from flask import Flask, request, render_template
from search import search
import html
from filter import Filter

app = Flask(__name__)

styles = """
<style>
.site {
  font-size: .8rem;
  color: green;  
}

.snippet {
  font-size: .9rem;
  color: grey
  margin-bottom: 30px
}
</style>
"""

search_template = styles + """
<form actions="/" method="POST">
   <input type="text" name="query">
   <input type="submit" value="Search">
</form>
"""

result_template = """
<p class="site">{rank}: {link}</p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""

def show_search_form():
  return search_template

def run_search(query):
  results = search(query)
  fi = Filter(results)

  filtered = fi.filter()
  
  rendered = search_template
  # Makes sure the html doesn't render the snipper
  print(filtered)
  print(filtered["snippet"])
  filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
  for index, row in filtered.iterrows():
    rendered += result_template.format(**row)

  return rendered

@app.route("/", methods=["GET", "POST"])
def search_form():
  if request.method == "POST":
    query = request.form["query"]
    return run_search(query)
  else:
    return show_search_form()

def run_page():
  app.run(host='0.0.0.0', port=9999)
