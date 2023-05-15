import csv
import argparse
from sys import argv, exit
##from tree import Tree

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = "CSV filename")
    args = parser.parse_args()

    if len(argv) == 1:
        exit(0)
    
    with open(args.filename,'rt') as file:

        exemples_reader = csv.reader(file)
        first_row = exemples_reader.__next__()

        exemples = []
        for line in exemples_reader:
            exemples.append(line)

        attributes = {} ## vai ser um dicionario em que a chave é uma string
        for position in range(len(first_row)):
            attributes[first_row[position]] = position
        
        label_class = first_row[-1]
        file.close()

    ##tree = Tree(exemples,attributes,label_class)
    print(attributes)

main()
