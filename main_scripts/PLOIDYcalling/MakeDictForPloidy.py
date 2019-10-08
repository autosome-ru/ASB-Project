
import requests
import json
def findLAB(enc):
    if enc.find(";") != -1:
        enc = enc.split(";")[0]
    if enc.find("wgEncode") == -1:
        r = requests.get('https://www.encodeproject.org/experiments/' + enc + '/?format=json')
        lab = json.loads(r.text)['lab']['@id']
        biosample = json.loads(r.text)['replicates'][0]['library']['biosample']['@id']
        ret=lab + "_"  + biosample
        return ret.replace("/","_")
    else:
        return ('False')

def CreatePath(line, ctrl=False):
    if ctrl:
        return ("/home/abramov/Alignments/CTRL/" + line[10] + "/" + line[14] + ".vcf.gz")
    else:
        return ("/home/abramov/Alignments/EXP/" + line[1] + "/" + line[0] + "/" + line[6] + ".vcf.gz")


def add_to_dict(d, key, value):
    el = d.get(key, None)
    if el:
        d[key] = el + [value]
    else:
        d[key] = [value]


def add_record(d, line, ctrl=False):
    if ctrl:
        idcs = (12, 15, 16)
    else:
        idcs = (4, 8, 9)
    
    path = CreatePath(line, ctrl)
    line[idcs[0]]=line[idcs[0]].replace("(","").replace(")","").replace(" ","_").replace("/","_")
    if line[idcs[2]] != "None":
        Lab = findLAB(line[idcs[2]])
        if Lab:
            key = line[idcs[0]] + '!' + Lab
            add_to_dict(d, key, path)
    elif line[idcs[1]] != "None":
        key = line[idcs[0]] + '!' + line[idcs[1]]
        add_to_dict(d, key, path)


def MakeDict(masterList):
    master = open(masterList, "r")
    d = dict()
    count = 0
    for line in master:
        count += 1
        if count % 5 == 0:
            print("Made {0} Experiments out of ~6120".format(count))
        l = line.strip().split("\t")
        add_record(d, l)
        
        if len(l) > 16:
            add_record(d, l, ctrl=True)
    print("Saving Dictionary")
    with open("/home/abramov/PLOIDYcalling/CELL_LINES.json", "w") as write_file:
        json.dump(d, write_file)
    print("Dictionary Saved")
MakeDict("/home/abramov/PLOIDYcalling/Master-lines.tsv")
