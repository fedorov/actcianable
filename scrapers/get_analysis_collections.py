import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

import backoff

import json

@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_time=60)
def get_url(url):#, headers):
  return requests.get(url) #, headers=headers)

URL = 'https://www.cancerimagingarchive.net/tcia-analysis-results/'
page = get_url(URL)

soup = BeautifulSoup(page.content, "html.parser")

table = soup.find(id="tablepress-10")

#print(table.prettify())

rows = table.find_all("tr")

table = []
header = "Collection,DOI,CancerType,Location,Subjects,Collections,AnalysisArtifactsonTCIA,Updated".split(",")

for row in rows:
  trow = {}
  cols = row.find_all("td")
  for cid, col in enumerate(cols):
    if cid == 0:
      trow[header[0]] = col.find("a").text
      trow[header[1]] = col.find("a")["href"]
    else:
      trow[header[cid+1]] = col.text
  if len(trow):
    table = table + [trow]

#print(tabulate(table, headers=header))

print(len(rows))

with open("output/analysis_collections.json", "w") as f:
  f.write(json.dumps(table, indent=2))
