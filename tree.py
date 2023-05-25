import math
from sys import maxsize
from copy import deepcopy

class Tree:

    def __init__(self, data_matrix, attributes, label_class):
        self.classe = label_class
        self.transformations = {} # dicionario com os intervalos de cada coluna (variavel) por ordem crescente
        self.possible_objectives = []

        for row in data_matrix:
            type_class = row[-1]
            if type_class not in self.possible_objectives:
                self.possible_objectives.append(type_class)

        self.attributes = attributes
        self.reverse_attributes = {} # exemplo : {0: 'ID', 1: 'sepallength', 2: 'sepalwidth', 3: 'petallength', 4: 'petalwidth', 5: 'class'}
        for key, position in attributes.items():
            self.reverse_attributes[position] = key

        # guarda os intervalos e o seu tipo do classe, para cada atributo do tipo inteiro
        for index in range(1,len(attributes)):
            try:
                float(data_matrix[0][index])
                self.set_intervalos(data_matrix, index)  
            except ValueError:
                pass

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

    def entropia(self, data_matrix):
        
        count_classes = {} # dicionário de tuplos para armazenar a quantidade de vezes que cada espécie aparece no csv e a sua respetiva entropia

        # calcular a quantidade de cada espécie

        for row in data_matrix:
            type_class = row[-1]
            if type_class not in count_classes:
                count_classes[type_class] = 1
            else:
                count_classes[type_class] += 1

        # calcular a entropia

        calculate_entropia = 0

        for key, value in count_classes.items():
            calculate_entropia += -(value / len(data_matrix)) * math.log2(value / len(data_matrix))
            calculate_entropia *= (value / len(data_matrix)) 
            count_classes[key] = (value, calculate_entropia)
            count_classes[key] = calculate_entropia
            calculate_entropia = 0
        print(count_classes) 

        

