import math
from copy import deepcopy


class Node:
    def __init__(self, attribute = None, label = None, is_leaf = False):
        self.attribute = attribute
        self.label = label
        self.is_leaf = is_leaf
        self.count = {}
        self.children = {}

    def recursive(self, node, space):
        result = ""
        if node.is_leaf:
                if isinstance(node.count, dict):
                    count_str = " ".join(f"{count}" for _, count in node.count.items())
                else:
                    count_str = str(node.count)
                result += f"{space}{node.label}({count_str})\n"
        else:
            sorted_children = sorted(node.children.items(), key = lambda x: x[0]) # ordenar os filhos por ordem crescente
            for value, child in sorted_children: # percorrer os filhos
                result += f"{space}{node.attribute}:{value}\n"
                result += self.recursive(child, space + "  ")
        return result

    def __str__(self):
        return self.recursive(self, " ")


class Tree:
    def __init__(self, data_matrix, attributes, label_class):
        self.dataset = data_matrix
        self.classe = label_class # nome da coluna da classe
        self.entropy_class = self.entropy([linha[-1] for linha in data_matrix]) # entropia da classe
        self.entropy_atrributes = {} # dicionario com a entropia de cada atributo

        self.attributes =   {}
        self.reverse_attributes = {} # exemplo : {1: 'sepallength', 2: 'sepalwidth', 3: 'petallength', 4: 'petalwidth', 5: 'class'}
        for key, position in attributes.items():
            if key != 'ID' and position != len(attributes) -1:
                self.reverse_attributes[position] = key
                self.attributes[key] = position

        self.attribute_entropy(data_matrix)
        self.root = self.build_tree(data_matrix, self.attributes) # construir a arvore de decisão

    def build_tree(self, data_matrix, attributes):
        labels = [linha[-1] for linha in data_matrix] # cria uma lista com as classes dos exemplos

        if len(set(labels)) == 1:
            leaf_node = Node(attribute=None)
            leaf_node.is_leaf = True
            leaf_node.label = labels[0]
            leaf_node.count = self._count_classes(data_matrix)
            return leaf_node

        if len(attributes) == 0:
            leaf_node = Node(attribute=None)
            leaf_node.is_leaf = True
            leaf_node.label = self.most_common_class(labels)
            leaf_node.count = len(labels)
            return leaf_node
        
        best_attribute = self.information_gain(data_matrix,attributes)

        root = Node(best_attribute)
        val = attributes[best_attribute]
        unique_values = list(set(linha[val] for linha in self.dataset))

        try:
            float(unique_values[0])
            best_split = self.calcule_best_split(data_matrix, best_attribute)
            subset_menor = [linha for linha in data_matrix if float(linha[attributes[best_attribute]]) <= float(best_split)]
            subset_maior  = [linha for linha in data_matrix if float(linha[attributes[best_attribute]]) > float(best_split)]
            new_attributes = attributes.copy()
            del new_attributes[best_attribute]
            root.children['<= ' + str(best_split)] = self.build_tree(subset_menor, new_attributes)
            root.children['> ' + str(best_split)] = self.build_tree(subset_maior, new_attributes)
        
        except ValueError:
            for value in unique_values:
                subset = [linha for linha in data_matrix if linha[attributes[best_attribute]] == value]
                if len(subset) > 0:
                    new_attributes = attributes.copy()
                    del new_attributes[best_attribute]
                    child_node = self.build_tree(subset, new_attributes)
                    root.children[value] = child_node
                else:
                    leaf_node = Node(attribute = None)
                    leaf_node.is_leaf = True
                    leaf_node.label = self.most_common_class(labels)
                    leaf_node.count = 0
                    root.children[value] = leaf_node
        return root
    
    def calcule_best_split(self, data_matrix, best_attribute):
        unique_values = list(set(linha[self.attributes[best_attribute]] for linha in data_matrix))
        best_split = ''
        best_info_gain = - math.inf

        if len(unique_values) == 1:
            return unique_values[0]
        
        for value in unique_values:
            subset_maior = []
            subset_menor = []
            for linha in data_matrix:
                if float(linha[self.attributes[best_attribute]]) <= float(value):
                    subset_menor.append(linha)
                if float(linha[self.attributes[best_attribute]]) > float(value):
                    subset_maior.append(linha)

            labels_menor = [linha[-1] for linha in subset_menor]
            labels_maior = [linha[-1] for linha in subset_maior]

            info_gain = self.split_info_gain([linha[-1] for linha in data_matrix], labels_menor, labels_maior)
            if info_gain > best_info_gain:
                best_info_gain = info_gain
                best_split = value
        return best_split

    def most_common_class(self, labels):
        class_counts = {} # dicionário com o número de ocorrências de cada classe
        for label in labels:
            if label not in class_counts:
                class_counts[label] = 1 # se a classe ainda não existir, criar uma entrada com o valor 1
            else:
                class_counts[label] += 1 # se a classe já existir, incrementar o valor
        return max(class_counts, key = class_counts.get)
    
    def split_info_gain(self, dataset, label_menor, label_maior):
        parent_entropy = self.entropy(dataset)
        probabily_menor = len(label_menor) / len(dataset)
        probabily_maior = len(label_maior) / len(dataset)
        entropy_menor = self.entropy(label_menor)
        entropy_maior = self.entropy(label_maior)
        value_info_gain = parent_entropy - (probabily_menor * entropy_menor) - (probabily_maior * entropy_maior)
        return value_info_gain

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
        for _, val in self.attributes.items():
            # attributes = {'sepallength': 1, 'sepalwidth': 2, 'petallength': 3, 'petalwidth': 4}
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

    def information_gain(self,data_matrix,attributes):
        info_gain = None
        best_value = 0
        value = 0
        for key, val in attributes.items():
            self.entropy_class = self.entropy([linha[-1] for linha in data_matrix])
            self.attribute_entropy(data_matrix)
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
        return class_counts 
    
    def tranform(self, data):
        results = []
        for row in data:
            result = self.tranform_tree(self.root, row)
            results.append(result)
        return results

    def tranform_tree(self, tree, row):
        if tree.is_leaf:
            return tree.label

        #print(tree.attribute)
        #print(row)
        #print(tree.children)
        attribute_value = row[tree.attribute]
        #print(attribute_value)

        try:
            attribute_value = float(attribute_value)
            #print(str(attribute_value) + " " + "Success")
            split_key = list(tree.children.keys())[0]
            split_operator, split_value = split_key.split(' ')
            subtree = tree.children

            if split_operator == '<=':
                try:
                    if float(attribute_value) <= float(split_value):
                        subtree = subtree['<= ' + split_value]
                    else:
                        subtree = subtree['> ' + split_value]
                except ValueError:
                    return None  # Non-numeric value, skip the comparison
            elif split_operator == '>':
                try:
                    if float(attribute_value) > float(split_value):
                        subtree = subtree['> ' + split_value]
                    else:
                        subtree = subtree['<= ' + split_value]
                except ValueError:
                    return None  # Non-numeric value, skip the comparison

            return self.tranform_tree(subtree, row)
        except ValueError:
            if attribute_value in tree.children:
                child = tree.children[attribute_value]
                return self.tranform_tree(child, row)
            else:
                # Handle missing attribute value or unseen attribute value
                return None


    def __str__(self):
        return str(self.root)
