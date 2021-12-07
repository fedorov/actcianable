import json

try:
  with open("ouput/clinical_collections.json","r") as fc:
    current_clinical = jsonload(fc)
  with open("ouput/clinical_notes.json","r") as fn:
    clinical_notes = jsonload(fn)
  
  for entry in current_clinical:
    colec = current_clinical['Collection']
    if colec in clinical_notes:
      entry['Notes'] = clinical_notes[colec]
 
   with open("ouput/clinical_collections.json","w") as fo:
    fo.write(json.dumps(current_clinical, indent=2))
expect IOError:
  print("error updating clinical notes")     
