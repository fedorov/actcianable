import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import backoff
import json
import os
import hashlib

@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_time=60)
def get_url(url):#, headers):
  return requests.get(url) #, headers=headers)



def fetchClinical(collection_name, collection_href, data_formats, filenms):
  colrequest = requests.get(collection_href, timeout=30)
  content = colrequest.content
  collection_html = BeautifulSoup(content, 'html.parser')
  data_access_rows = collection_html.find('div',{'name':'Data Access'}).find('tbody').find_all('tr')
  some_external=False
  access_error=True
  some_internal=False
  for da_row in data_access_rows:
    tds= da_row.find_all('td')
    if (len(tds)>0):
      data_type =tds[0].text.strip()
      # data_type reported as 'clinical' in the 'Data Type' column means there is clinical data
      if ('alternate' in current_clinical[collection_name]):
        i=1
        pass

      if ( (data_type.lower().find('clinical')>-1) or  (('alternate' in current_clinical[collection_name]) and (data_type in current_clinical[collection_name]['alternate']))):
        #clinical_found = True
        #print(collection_name+" "+data_type)
        hrefArr = tds[1].find_all('a', href=True)
        for href in hrefArr:
          download_file_found_in_row=False
          filenm=''
          url = href.attrs['href']
          purl = urlparse(url)
          #add tcia hostname to internal links
          if purl.hostname is None:
            url = tcia_protocol+tcia + url
            purl = urlparse(url)
          # some download urls links not on tcia
          if (purl.hostname.find(tcia) == -1):
            some_external = True
          else:
            some_internal = True
            try:
              print(url)
              head_info = requests.head(url, timeout=5)
              # if the 'download' link does not include a 'Content-Disposition' header this likely means that the link does NOT resolve to a downloadable file
              if ('Content-Disposition' in head_info.headers) and (head_info.headers['Content-Disposition'].find('filename=') > -1):
                  filenm = head_info.headers['Content-Disposition'].split("filename=")[1].replace('"', '')
                  ext = os.path.splitext(filenm)[1].lower()
                  data_formats.add(ext)
                  resp = requests.get(url)
                  md5 = hashlib.md5(resp.content).hexdigest()
                  filenms.append('<a href="' + url + '">' + filenm + '</a>: ' + md5)
                  dirname = collection_name.replace('/', '_')
                  path = 'output/clinical_files/' + dirname
                  if not os.path.exists(path):
                      os.makedirs(path)
                  with open(path + '/' + filenm, 'wb') as f:
                      f.write(resp.content)
              else:
                access_error = True
            except:
              access_error = True
  if not some_internal:
    some_external = True
  return([access_error,some_internal])


notes={}
current_clinical={}
try:
  with open("output/clinical_notes.json", "r") as f:
    current_clinical=json.load(f)
    for colec in current_clinical:
      if 'notes' in current_clinical[colec]:
        notes[colec] = current_clinical[colec]['notes']
except IOError:
    print("clinical notes file not found")

tcia_protocol='https://'
tcia= 'wiki.cancerimagingarchive.net'
URL = 'https://www.cancerimagingarchive.net/collections/'
page = get_url(URL)
soup = BeautifulSoup(page.content, "html.parser")
tableb = soup.find(id="tablepress-9").find('tbody')
rows = tableb.find_all("tr")
outTable = []

header = "Collection,DOI,Wiki,Format,Filenames,Notes".split(",")

for row in rows:
  trow = {}
  cols = row.find_all("td")
  collection_col = row.find('td',{'class':'column-1'})
  collection_name = collection_col.text.strip()
  collection_href = collection_col.find('a').attrs['href']
  if collection_href.startswith('//'):
      collection_href = 'https:' + collection_href

  collection_supporting_col = row.find('td',{'class':'column-7'})
  collection_supporting = collection_supporting_col.text.strip()

  if (('Clinical' in collection_supporting) or (collection_name in current_clinical)):
    if not (collection_name in current_clinical):
        current_clinical[collection_name]={}

        current_clinical[collection_name]['notes'] ='collection not yet curated for idc'
        notes[collection_name] = current_clinical[collection_name]['notes']

    data_formats=set()
    filenms=[]
    some_internal=False
    try:
      [access_error, some_internal] = fetchClinical(collection_name, collection_href, data_formats, filenms)
    except:
      print("problem scraping page for this collection: "+ collection_name+" "+collection_href)
      access_error=True

    data_formats_list=list(data_formats)
    data_formats_list.sort()
    data_format_str= ", ".join(data_formats_list)
    filenms.sort()
    filenm_str= ", ".join(filenms)
    trow[header[0]] = collection_name
    trow[header[1]] = collection_href
    trow[header[2]] = some_internal
    trow[header[3]]=data_format_str
    trow[header[4]] = filenm_str
    try:
      trow[header[5]] = notes[collection_name]
    except:
      trow[header[5]]=""
    if access_error:
        trow[header[5]] = trow[header[5]]+"!Run Time Error: Collection not scraped!"
    outTable= outTable + [trow]

with open("output/clinical_collections.json", "w") as f:
  f.write(json.dumps(outTable, indent=2))




