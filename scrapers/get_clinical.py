import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import backoff

import json

@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_time=60)
def get_url(url):#, headers):
  return requests.get(url) #, headers=headers)


def discover_format(purl, data_type):
    data_format_str='NA'

    if (purl.path.lower().find('.txt') >-1):
        data_format_str='TXT'
    elif (purl.path.lower().find('.xlsx') >-1):
        data_format_str='XLSX'
    elif (purl.path.lower().find('.xlsb') >-1):
        data_format_str='XLSB'
    elif (purl.path.lower().find('.xls') >-1):
        data_format_str='XLS'
    elif (purl.path.lower().find('/api/') >-1):
        data_format_str='JSON'
    elif (purl.path.lower().find('.csv') >-1):
        data_format_str='CSV'
    elif (data_type.lower().find('csv') > -1):
        data_format_str='CSV'
    elif (data_type.lower().find('txt') > -1):
        data_format_str='TXT'
    elif (data_type.lower().find('xls') > -1):
        data_format_str='XLS'

    elif (data_type.lower().find('api') > -1):
        data_format_str='API'
    elif (data_type.lower().find('json') > -1):
        data_format_str='JSON'

    return(data_format_str)


URL = 'https://www.cancerimagingarchive.net/collections/'
page = get_url(URL)

soup = BeautifulSoup(page.content, "html.parser")

tableb = soup.find(id="tablepress-9").find('tbody')

#print(table.prettify())

rows = tableb.find_all("tr")
#print("rows "+str(len(rows)))


outTable = []
header = "Collection,DOI,DataType,Format,Compression,IsExternal,Links,".split(",")

for row in rows:
  trow = {}
  #print(row.prettify())
  cols = row.find_all("td")
  #print(str(len(cols)))
  collection_col = row.find('td',{'class':'column-1'})
  collection_name = collection_col.text.strip()
  collection_href = collection_col.find('a').attrs['href']
  if collection_href.startswith('//'):
      collection_href = 'https:' + collection_href
      colrequest = requests.get(collection_href)
      content = colrequest.content
      collection_html = BeautifulSoup(content, 'html.parser')
      data_access_rows = collection_html.find('div',{'name':'Data Access'}).find('tbody').find_all('tr')
      for da_row in data_access_rows:
          tds= da_row.find_all('td')
          if (len(tds)>0):
              data_type =tds[0].text.strip()
              linkArr=tds[1].find_all('a', href=True)
              if (data_type.lower().find('clinical')>-1):
                  trow={}
                  trow[header[0]] = collection_name
                  trow[header[1]] = collection_href
                  comp='None'
                  external='false'
                  data_format_str='NA'

                  #Usually there is only one download link per row in data tables. Often there is another link to a data portal
                  downloadLinks=[]
                  linkArr = tds[1].find_all('a', href=True)
                  for link in linkArr:
                      url=link.attrs['href']
                      if (len(linkArr) == 1) or (url.lower().find('download')>-1):
                          downloadLinks.append(url)
                          purl=urlparse(url)
                          if (purl.hostname is not None) and (purl.hostname.find('cancerimagingarchive')==-1):
                              external = 'true'
                              data_format_str=discover_format(purl,data_type)
                  downloadLinksH=['<a href="'+link+'">'+link+'</a>' for link in downloadLinks]
                  downloadLinkStr = '<br>'.join(downloadLinksH)

                  if (downloadLinkStr.find('cancerimagingarchive')==-1):
                       external = 'true'

                  trow[header[2]]=data_type
                  trow[header[3]]=data_format_str
                  trow[header[4]]=comp
                  trow[header[5]]=external
                  trow[header[6]]=downloadLinkStr
                  if len(trow):
                      outTable= outTable + [trow]
                                                           
print(len(outTable))
with open("output/clinical_collections.json", "w") as f:
  f.write(json.dumps(outTable, indent=2))                        
                    
                


