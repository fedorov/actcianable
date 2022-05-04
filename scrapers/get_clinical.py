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

notes={}
try:
  with open("output/clinical_notes.json", "r") as f:
    current_clinical=json.load(f)
    for colec in current_clinical:
      if 'notes' in current_clinical[colec]:
        notes[colec] = current_clinical[colec]['notes']

except IOError:
    print("clinical notes file not found")



tcia= 'https://wiki.cancerimagingarchive.net'
URL = 'https://www.cancerimagingarchive.net/collections/'
page = get_url(URL)
soup = BeautifulSoup(page.content, "html.parser")
tableb = soup.find(id="tablepress-9").find('tbody')
rows = tableb.find_all("tr")
outTable = []

header = "Collection,DOI,Format,External,Download,Filenames,Notes".split(",")

for row in rows:
  trow = {}
  cols = row.find_all("td")
  collection_col = row.find('td',{'class':'column-1'})
  collection_name = collection_col.text.strip()
  collection_href = collection_col.find('a').attrs['href']
  if collection_href.startswith('//'):
      collection_href = 'https:' + collection_href

  colrequest = requests.get(collection_href, timeout=30)
  content = colrequest.content
  collection_html = BeautifulSoup(content, 'html.parser')
  data_access_rows = collection_html.find('div',{'name':'Access'}).find('tbody').find_all('tr')
  clinical_found = False
  some_clinical_downloadable = False
  some_clinical_not_downloadable = False
  some_clinical_external = False
  data_formats = set()
  filenms = []
  for da_row in data_access_rows:
    tds= da_row.find_all('td')
    if (len(tds)>0):
      data_type =tds[0].text.strip()

      # data_type reported as 'clinical' in the 'Data Type' column means there is clinical data
      if (data_type.lower().find('clinical')>-1):

        clinical_found = True
        #print(collection_name+" "+data_type)
        hrefArr = tds[1].find_all('a', href=True)
        for href in hrefArr:
          download_file_found_in_row=False
          filenm=''
          url = href.attrs['href']
          purl = urlparse(url)
          #add tcia hostname to internal links
          if purl.hostname is None:
            url = tcia + url
            purl = urlparse(url)
          # some download urls links not on tcia
          if (purl.hostname.find('cancerimagingarchive') == -1):
            some_clinical_external = True
          # check header before trying to download file
          try:
            head_info = requests.head(url, timeout=5)
            successReq = True
          except:
              successReq = False
          # if the 'download' link does not include a 'Content-Disposition' header this likely means that the link does NOT resolve to a downloadable file but to a web portal or json content
          if (successReq) and ('Content-Disposition' in head_info.headers) and (head_info.headers['Content-Disposition'].find('filename=') > -1):
            some_clinical_downloadable = True
            download_file_found_in_row = True
            filenm = head_info.headers['Content-Disposition'].split("filename=")[1].replace('"', '')
            ext = os.path.splitext(filenm)[1].lower()
            data_formats.add(ext)
          # clinical data may in a json resource
          elif (successReq) and ('Content-Type' in head_info.headers) and (head_info.headers['Content-Type'].find('json')>-1):
            some_clinical_downloadable = True
            download_file_found_in_row = True
            filenm = url.replace('https://','')
            filenm = filenm.replace('http://', '')
            filenm = filenm.replace('/', '_')
            data_formats.add('.json')
          if download_file_found_in_row:
            resp = requests.get(url)
            md5=hashlib.md5(resp.content).hexdigest()
            filenms.append('<a href="'+url+'">'+filenm+'</a>: '+md5)
            dirname=collection_name.replace('/','_')
            path='output/clinical_files/'+dirname
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path+'/'+filenm, 'wb') as f:
              f.write(resp.content)
          else:
              some_clinical_not_avail = True

  if clinical_found:
    data_formats_list=list(data_formats)
    data_formats_list.sort()
    data_format_str= ", ".join(data_formats_list)
    filenms.sort()
    filenm_str= ", ".join(filenms)
    avail=""
    if some_clinical_downloadable:
      if some_clinical_not_downloadable:
        avail="partial"
      else:
        avail="yes"
    else:
      avail="no"
    trow[header[0]] = collection_name
    trow[header[1]] = collection_href
    trow[header[2]]=data_format_str
    trow[header[3]]=some_clinical_external
    trow[header[4]] = avail
    trow[header[5]] = filenm_str
    if collection_name in notes:
      trow[header[6]] = notes[collection_name]
    else:
      trow[header[6]] = ''

  if len(trow):
    outTable= outTable + [trow]

#print(len(outTable))
with open("output/clinical_collections.json", "w") as f:
  f.write(json.dumps(outTable, indent=2))




