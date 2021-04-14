import pandas as pd
import json

with open('output/collections.json', 'r') as f:
  #cont = f.read()
  #print(cont)
  #print(cont)
  collections_df = pd.read_json(f, orient='records')

with open('output/image_analyses_details.json', 'r') as f:
  #cont = f.read()
  #print(cont)
  #print(cont)
  analyses_details_df = pd.read_json(f, orient='records')

with open('output/status.json', 'r') as f:
  #cont = f.read()
  #print(cont)
  #print(cont)
  status_df = pd.read_json(f, orient='records')

#print(analyses_details_df.columns)
#print(collections_df.columns)

#print(analyses_details_df['DOI'])
#print('---')
#print(collections_df['DOI'])

#analyses_details_df.set_index('DOI').join(collections_df.set_index('DOI'))
analyses_details_df.columns
print("After")
merged_df = analyses_details_df.merge(collections_df, on=['DOI'])[["Collection_x","DOI","Subjects","Updated","Format","DICOMstatus","Comment","CollectionType", "DICOMtarget"]]

print(merged_df.columns)
merged_df.rename(columns={"Collection_x":"Collection"}, inplace=True)

print(merged_df.columns)

with open('output/image_analyses_view.json', 'w') as f:
  df_dict = merged_df.to_dict(orient='records')
  df_json = json.dumps(df_dict, indent=2)
  f.write(df_json)

merged_df = collections_df.merge(idc_collection_status, on=["Collection"], how="left")[["Collection", "DOI", "Access", "some_date", "is_excluded"]]
with open('output/status_view.json', 'w') as f:
  df_dict = merged_df.to_dict(orient='records')
  df_json = json.dumps(df_dict, indent=2)
  f.write(df_json)
