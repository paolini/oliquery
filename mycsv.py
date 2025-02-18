def dotted_field(d,field):
  for f in field.split('.'):
    if not d:
      return None
    d = d.get(f)
  return d

def sanitize(s):
    if type(s) == bool:
       return "1" if s else "0"
    if not hasattr(s, "replace"):
        s = str(s)
    return s.replace("\n", " ").replace("\r", " ").replace("\t", " ")

def tsv_row(row, fields):
  return "\t".join([sanitize(dotted_field(row,field)) for field in fields])

def tsv_header(fields):
  return "\t".join(fields)

def csv_escape(s):
  return '"' + s.replace('"', '""') + '"'

def csv_row(row, fields):
  return ",".join([csv_escape(sanitize(dotted_field(row,field))) for field in fields])

def csv_header(fields):
  return ",".join([csv_escape(field) for field in fields])
