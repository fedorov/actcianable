import json

try:
  with open("output/clinical_collections.json","r") as fc:
    current_clinical = json.load(fc):quit()
  with open("output/clinical_notes.json","r") as fn:
    clinical_notes = json.load(fn)

  for entry in current_clinical:
    colec = entry['Collection']
    if colec in clinical_notes:
      entry['Notes'] = clinical_notes[colec]

  with open("output/clinical_collections.json","w") as fo:
    fo.write(json.dumps(current_clinical, indent=2))
except IOError:
  print("error updating clinical notes")
