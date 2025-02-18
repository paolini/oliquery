#import pandas as pd
import json

#filejsonl = "~/Downloads/Telegram\ Desktop/students.jsonl"
filejsonl = "2024Archimede-biennio-nov-students20241221.jsonl"
#fileout = "statsparziali-err.txt"

with open(filejsonl, "r") as j_file:
    datistud = list(j_file)

#datistud = pd.read_json(path_or_buf = filejsonl, lines = True)
opz0 = ["2", "3", "4", "5"]
opz1 = ["1", "2", "3", "4", "5"]
opz2 = ["1", "2", "3", "4", "5", "6", "7", "8"]
opza = ["A", "B", "C", "D", "E", "-", "X"]

for jline in datistud:
    jd = json.loads(jline)
    excl = False
    if "disabled" in jd and jd["disabled"] is True:
        excl = True
        e = "Exc"
    else:
        e = "Inc"
    if "school" in jd:
        sc = jd["school"]
    else:
        sc = jd["participationId"][:10]
    s = ""
    anaval = True
    ana = {}
    if "personalInformation" in jd and jd["personalInformation"] is not None:
        ana = jd["personalInformation"]
    if "userData" in jd and jd["userData"] is not None:
        ana = jd["userData"]
    if ana != {}:
        anaasscount = 0
        if "surname" in ana and ana["surname"] != "":
            s = s + " " + ana["surname"]
        else:
            anaasscount += 1
            anaval = False
            s = s + " -cognome- "
        if "name" in ana and ana["name"] != "":
            s = s + " " + ana["name"]
        else:
            anaasscount += 1
            anaval = False
            s = s + " -nome- "
        if "classYear" in ana and ana["classYear"] != "":
            s = s + " " + str(ana["classYear"])
        else:
            anaasscount += 1
            anaval = False
            s = s + " -anno- "
        if "classSection" in ana and ana["classSection"] != "":
            s = s + " " + ana["classSection"]
        else:
            anaasscount += 1
            anaval = False
            s = s + " -sez- "
        if "birthDate" in ana and ana["birthDate"] != "":
            s = s + " okDataNasc "
        else:
            anaasscount += 1
            anaval = False
            s = s + " -nato/a- "
    else:
        anaasscount = 5
        anaval = False
        s = s + " ---  --  --  --  -- "
    an = "anaOK "
    if not anaval:
        if anaasscount < 5:
            an = "anaManc "
        else:
            an = "anaAss "
    v = ""
    varass = False
    varValid = True
    if "variant" not in jd or jd["variant"] == None or jd["variant"] == "":
        varass = True
        v = "mancaCod "
    else:
        v = jd["variant"]
        if v[0] not in opz0 or v[1] not in opz1 or v[2] not in opz2:
            varValid = False
    t = ""
    rispval = True
    notrisp = False
    vuote = False
    nonvuote = False
    na = 0
    if "answers" not in jd:
        notrisp = True
    else:
        for ai in jd["answers"]:
            a = jd["answers"][ai]
            na += 1
            if a is not None and a != "":
                nonvuote = True
                if str(a).upper() not in opza:
                    rispval = False
                    t = t + "Z"
                else:
                    t = t + a
            else:
                vuote = True
                if a is None:
                    t = t + "N"
                else:
                    t = t + "."
            #t = t + " |"

    print(sc + " " + e, end=" ")
    if anaasscount == 5 and varass and notrisp:
        print(" riga vuota ", end=" ")
        print("+", end=" ")
    elif anaasscount == 5 and varass and vuote and not nonvuote:
        print(" riga vuota ", end=" ")
        print("+", end=" ")
    else:
        print(an, end=" ")
        if varass:
            print("mancaCodice", end=" ")
        elif varValid:
            print("OkCodice", end=" ")
        else:
            print("noValCodice", end = " ")
        if not nonvuote:
            print(" nessunaRisp", end=" ")
        elif vuote:
            print(" qualcheRispVuota", end=" ")
            if not rispval:
                print(" qualcheNonValida", end=" ")
        elif not rispval:
            print(" qualcheNonValida", end=" ")
        else:
            print(" rispValide", end=" ")
        print(" +", end=" ")

        print(s + " " + v, end=" ")
    print("| " + t + " |", end=" ")
    print("++ " + jd["id"], end=" ")
    print(na, end=" ")
    print("")
