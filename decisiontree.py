import csv
import argparse
from sys import argv, exit
from tree import Tree

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help = "CSV filename")
    args = parser.parse_args()

    if len(argv) == 1:
        exit(0)

    with open(args.filename,'rt') as file:

        data_matrix_reader = csv.reader(file)
        first_row = data_matrix_reader.__next__()

        data_matrix = [] # matriz em que em cada posição está cada linha do csv
        for line in data_matrix_reader:
            data_matrix.append(line)

        attributes = {}  # vai ser um dicionario em que cada chave é o nome da variável de cada coluna (string)
        # exemplo : {'ID': 0, 'sepallength': 1, 'sepalwidth': 2, 'petallength': 3, 'petalwidth': 4, 'class': 5}
        for position in range(len(first_row)):
            attributes[first_row[position]] = position

        label_class = first_row[-1]
        file.close()

    tree = Tree(data_matrix, attributes, label_class)

    print(tree.root)

main()
