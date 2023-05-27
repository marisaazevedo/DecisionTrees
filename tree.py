import math
from sys import maxsize
from copy import deepcopy

class Tree:

    def __init__(self, data_matrix, attributes, label_class):
        self.classe = label_class
        self.transformations = {} # dicionario com os intervalos de cada coluna (variavel) por ordem crescente
        self.possible_objectives = []
        self.entropy_class = self.entropy([linha[-1] for linha in data_matrix])
        self.entropy_atrributes = {}

        for row in data_matrix:
            type_class = row[-1]
            if type_class not in self.possible_objectives:
                self.possible_objectives.append(type_class)

        self.attributes = attributes
        self.reverse_attributes = {} # exemplo : {0: 'ID', 1: 'sepallength', 2: 'sepalwidth', 3: 'petallength', 4: 'petalwidth', 5: 'class'}
        for key, position in attributes.items():
            self.reverse_attributes[position] = key

        # guarda os intervalos e o seu tipo do classe, para cada atributo do tipo inteiro
        for index in range(1, len(attributes)):
            try:
                float(data_matrix[0][index])
                self.set_intervalos(data_matrix, index)
            except ValueError:
                pass
        self.attribute_entropy(data_matrix)
        self.info_gain = self.information_gain()

    def set_intervalos(self, data_matrix , index):  # guardo os intervalos e o seu tipo do classe, para um  atributo.

        list_number = [] # guardar todas os valores de uma coluna especifica do csv e ao nome da 'classe' dessa mesma linha

        for i in range(len(data_matrix)):
            list_number.append((float(data_matrix[i][index]), data_matrix[i][-1]))

        list_number.sort() # organiza por ordem crescente

        intervalo = []
        i = 0

        for value, label in list_number:
            if i == 0:
                min_value = value
                a_label = label
            elif i > 0 :
                if a_label != label:
                    intervalo.append((min_value, value, label))
                    i = 0
                    min_value = value
                    a_label = label
                else:
                    i = 0
            i += 1

        intervalo.append((min_value, value + 0.1, label))

        self.transformations[self.reverse_attributes[index]] = intervalo


    def entropy(self, data_label):
        count_classes = {}
        total = len(data_label)
        entropy = 0

        for value in data_label:
            if  value not in count_classes:
                count_classes[value] = 1
            else:
                count_classes[value] += 1
        for value in count_classes.values():
            entropy += -(value / total) * math.log2(value / total)

        return entropy

    def attribute_entropy(self, data_matrix):

        for key, val in self.attributes.items():

            # attributes = {'ID': 0, 'sepallength': 1, 'sepalwidth': 2, 'petallength': 3, 'petalwidth': 4, 'class': 5}
            self.entropy_atrributes[0] = 0
            if key is not self.classe and key != 'ID': # verifica se o atributo não é a classe (ou seja, o atributo de destino) e não é a coluna 'ID'
                unique_attributes = list(set(linha[val] for linha in data_matrix)) # armazenar os valores daquele atributo numa lista
                entropy = 0
                for value in unique_attributes:
                    subset = []
                    for i in range(len(data_matrix)):
                        if(data_matrix[i][val] == value):
                            subset.append(data_matrix[i][-1])
                    subset_entropy = self.entropy(subset) # entropia do subconjunto de classes correspondentes ao valor atual do atributo
                    subset_probability = len(subset)/ len(data_matrix) # proporção de exemplos no subconjunto em relação ao conjunto de dados original
                    entropy += subset_probability * subset_entropy # atualizar a entropia total do atributo
                self.entropy_atrributes[val] = entropy # armazenar a entropia do atributo no dicionário


    def information_gain(self):
        info_gain = ''
        best_value = 0
        value = 0
        for key, val in self.attributes.items():
            if key is not self.classe and key != 'ID':
                value = self.entropy_class - self.entropy_atrributes[val]
                if value > best_value:
                    best_value = value
                    info_gain = key
        return info_gain
