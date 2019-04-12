import csv

def read_usda(file):
    return list(csv.reader(open(file, encoding="latin-1"), quotechar="~", delimiter="^"))

def write_list(file, list):
    f = open(file, "w")
    writer = csv.writer(f)
    for line in list:
        writer.writerow(line)

def write_typed_list(file, list, types):
    f = open(file, "w")
    writer = csv.writer(f)
    writer.writerow(types)
    for line in list:
        writer.writerow(line)
