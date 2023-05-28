import math
from copy import deepcopy


class Node:
    def __init__(self, attribute = None, label = None, is_leaf = False):
        self.attribute = attribute
        self.label = label
        self.is_leaf = is_leaf
        self.count = {}
        self.children = {}

    def add_child(self, value, child):
        self.children[value] = child

    def _str_recursive(self, node, indent):
        result = ""
        if node.is_leaf:
            # caso seja uma folha, imprimir o nome da classe e o número de ocorrências
            class_counts = node.count # dicionário com o número de ocorrências de cada classe
            count_str = " ".join(f"{count}" for _, count in class_counts.items())
            result += f"{indent}{node.label} ({count_str})\n"
        else:
            sorted_children = sorted(node.children.items(), key = lambda x: x[0]) # ordenar os filhos por ordem crescente
            for value, child in sorted_children: # percorrer os filhos
                if isinstance(value, tuple): # se o valor for um intervalo
                    result += f"{indent}{node.attribute}\n" # imprimir o nome do atributo
                    result += self._format_interval(value, indent + "    ") # imprimir o intervalo
                    result += self._str_recursive(child, indent + "        ")
                else:
                    result += f"{indent}{node.attribute}: {value}\n" # imprimir o nome do atributo e o valor
                    result += self._str_recursive(child, indent + "    ")
        return result

    def _format_interval(self, interval, indent):
        min_val, max_val = interval
        return f"{indent}{min_val} <= x < {max_val}:\n"

    def __str__(self):
        return self._str_recursive(self, "")



class Tree:
    def __init__(self, data_matrix, attributes, label_class):
        self.dataset = data_matrix
        self.classe = label_class # nome da coluna da classe
        self.transformations = {} # dicionario com os intervalos de cada coluna (variavel) por ordem crescente
        self.possible_objectives = [] # lista com os possiveis valores da classe
        self.entropy_class = self.entropy([linha[-1] for linha in data_matrix]) # entropia da classe
        self.entropy_atrributes = {} # dicionario com a entropia de cada atributo

        for row in data_matrix:
            type_class = row[-1]
            if type_class not in self.possible_objectives:
                self.possible_objectives.append(type_class)

        self.attributes =   {}
        self.reverse_attributes = {} # exemplo : {0: 'ID', 1: 'sepallength', 2: 'sepalwidth', 3: 'petallength', 4: 'petalwidth', 5: 'class'}
        for key, position in attributes.items():
            if key != 'ID':
                self.reverse_attributes[position] = key
                self.attributes[key] = position

        # guarda os intervalos e o seu tipo do classe, para cada atributo do tipo inteiro
        for index in range(1, len(attributes)):
            try:
                float(data_matrix[0][index])
                self.set_intervalos(data_matrix, index)
            except ValueError:
                pass
        self.attribute_entropy(data_matrix)
        self.info_gain = self.information_gain(self.attributes) # atributo com maior ganho de informação
        self.root = self.build_tree(data_matrix, self.attributes) # construir a arvore de decisão

    def build_tree(self, data_matrix, attributes):
        labels = [linha[-1] for linha in data_matrix] # cria uma lista com as classes dos exemplos

        if len(set(labels)) == 1: # se todos os exemplos pertencem à mesma classe
            # criar um nó folha com essa classe
            leaf_node = Node(attribute = None)
            leaf_node.is_leaf = True
            leaf_node.label = labels[0]
            leaf_node.count = self._count_classes(data_matrix)
            return leaf_node


        if len(attributes) <= 1: # se não existirem mais atributos para dividir
            # criar um nó folha com a classe mais comum
            leaf_node = Node(attribute = None)
            leaf_node.is_leaf = True
            leaf_node.label = labels
            return leaf_node


        best_attribute = self.information_gain(attributes) # calcula o atributo com maior ganho de informação
        root = Node(best_attribute) # cria um nó com esse atributo
        val = attributes[best_attribute] # posição do atributo na matriz de dados
        unique_values = list(set(linha[val] for linha in data_matrix)) # valores únicos do atributo
        if unique_values == []: # se não existirem valores únicos
            # criar um nó folha com a classe mais comum
            leaf_node = Node(attribute = None)
            leaf_node.is_leaf = True
            leaf_node.label = labels
            return leaf_node

        try:
            float(unique_values[-1]) # se o último valor for um número
            for menor, maior, _ in self.transformations[best_attribute]: # percorrer os intervalos
                subset = [] # subconjunto de exemplos que pertencem ao intervalo
                for linha in data_matrix:
                    if float(linha[attributes[best_attribute]]) >= menor and float(linha[attributes[best_attribute]]) < maior:
                        # se o valor do atributo estiver dentro do intervalo
                        subset.append(linha)
                new_attributes = attributes.copy() # cria uma cópia dos atributos
                del new_attributes[best_attribute] # remover o atributo atual
                child_node = self.build_tree(subset, new_attributes) # construir a árvore com o subconjunto
                root.children[menor] = child_node # adicionar o nó filho ao nó atual

        except ValueError: # se o último valor não for um número
            for value in unique_values: # percorrer os valores únicos
                subset = [linha for linha in data_matrix if linha[attributes[best_attribute]] == value] # subconjunto de exemplos que pertencem ao valor
                if len(subset) == 0: # se o subconjunto for vazio
                    # criar um nó folha com a classe mais comum
                    leaf_node = Node(attribute = None)
                    leaf_node.is_leaf = True
                    leaf_node.label = self.most_common_class(labels)
                    root.children[value] = leaf_node
                else:
                    new_attributes = attributes.copy() # cria uma cópia dos atributos
                    del new_attributes[best_attribute] # remover o atributo atual
                    child_node = self.build_tree(subset, new_attributes) # construir a árvore com o subconjunto
                    root.children[value] = child_node # adicionar o nó filho ao nó atual

        return root

    def most_common_class(self, labels):
        class_counts = {} # dicionário com o número de ocorrências de cada classe
        for label in labels:
            if label not in class_counts:
                class_counts[label] = 1 # se a classe ainda não existir, criar uma entrada com o valor 1
            else:
                class_counts[label] += 1 # se a classe já existir, incrementar o valor
        return max(class_counts, key = class_counts.get)

    def set_intervalos(self, data_matrix , index):  # guarda os intervalos e o seu tipo do classe, para um  atributo

        list_number = [] # guardar todas os valores de uma coluna especifica do csv e ao nome da 'classe' dessa mesma linha

        for i in range(len(data_matrix)):
            list_number.append((float(data_matrix[i][index]), data_matrix[i][-1]))

        list_number.sort() # organiza por ordem crescente

        intervalo = []
        i = 0

        for value, label in list_number: # percorrer os valores e as classes
            if i == 0: # se for o primeiro valor
                min_value = value # guardar o valor mínimo
                a_label = label # guardar a classe
            elif i > 0 : # se não for o primeiro valor
                if a_label != label: # se a classe for diferente da anterior
                    intervalo.append((min_value, value, label)) # adicionar o intervalo à lista
                    i = 0 # reiniciar o contador
                    min_value = value # atualizar o valor mínimo
                    a_label = label # atualizar a classe
                else:
                    i = 0
            i += 1

        intervalo.append((min_value, value + 0.1, label))

        self.transformations[self.reverse_attributes[index]] = intervalo


    def entropy(self, data_label): # calcula a entropia de um conjunto de classes
        count_classes = {} # dicionário com o número de ocorrências de cada classe
        total = len(data_label) # número total de exemplos
        entropy = 0

        for value in data_label:
            if value not in count_classes:
                count_classes[value] = 1 # se a classe ainda não existir, criar uma entrada com o valor 1
            else:
                count_classes[value] += 1 # se a classe já existir, incrementar o valor
        for value in count_classes.values():
            entropy += -(value / total) * math.log2(value / total) # calcular a entropia

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

    def information_gain(self,attributes):
        info_gain = None
        best_value = 0
        value = 0
        for key, val in attributes.items():
            if key is not self.classe and key != 'ID':
                value = self.entropy_class - self.entropy_atrributes[val] # calcular o ganho de informação
                if value > best_value: # se o ganho de informação for maior que o anterior
                    best_value = value # atualizar o melhor ganho de informação
                    info_gain = key # atualizar o melhor atributo
        return info_gain

    def _count_classes(self, dataset):
        class_counts = {}
        for data in dataset:
            label = data[-1]
            if label in class_counts:
                class_counts[label] += 1
            else:
                class_counts[label] = 1
        return class_counts # dicionário com o número de ocorrências de cada classe

    def __str__(self):
        return str(self.root)
