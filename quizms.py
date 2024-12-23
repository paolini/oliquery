import json

fields =[
    "id",
    "schoolId",
    "contestId",
    "name",
    "teacher",
    "finalized",
    "pdfVariants",
]

print("\t".join(fields))
for filename in [
    "participations-biennio-1",
    "participations-biennio-2",
    "participations-triennio-1",
    "participations-triennio-2"]:
    with open(filename+".jsonl") as f:
        for line in f:
            data = json.loads(line)
            row = [str(data.get(field, "")) for field in fields]
            print("\t".join(row))
