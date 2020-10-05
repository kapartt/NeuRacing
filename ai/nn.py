from random import random
from ai import utils


class NeuralNetwork:
    def __init__(self, layers: tuple = (), input_sz: int = 1, output_sz: int = 1, bias: bool = False,
                 max_w_value: float = 0.1, learning_rate: float = 0.1, lamda: float = 0,
                 dropout: float = 0, file_name: str = None):
        self.layers = layers
        self.input_sz = input_sz
        self.output_sz = output_sz
        self.weights = []
        self.learning_rate = learning_rate
        self.delta = []
        self.lamda = lamda
        self.dropout = dropout
        if file_name is None:
            self.layers = layers
            self.input_sz = input_sz
            self.output_sz = output_sz
            self.bias = bias
            self.weights = []
            for lay in range(len(layers) + 1):
                if lay == 0:
                    sz_0 = input_sz
                else:
                    sz_0 = layers[lay - 1]
                if bias:
                    sz_0 += 1
                sz_1 = output_sz
                if lay < len(layers):
                    sz_1 = layers[lay]
                w = []
                for i in range(sz_1):
                    d = []
                    for j in range(sz_0):
                        d.append((random() * 2 - 1) * max_w_value)
                    w.append(d)
                self.weights.append(w)
        else:
            f = open(file_name, 'r', encoding='utf-8')
            self.input_sz, self.output_sz, b = map(int, f.readline().rstrip().split(';'))
            if b == 0:
                self.bias = False
            else:
                self.bias = True
            self.learning_rate, self.lamda, self.dropout = map(float, f.readline().rstrip().split(';'))
            ln = f.readline().rstrip()
            if len(ln) > 0:
                self.layers = tuple(map(int, ln.split(';')))
            else:
                self.layers = ()
            for lay in range(len(self.layers) + 1):
                sz_1 = self.output_sz
                if lay < len(self.layers):
                    sz_1 = self.layers[lay]
                w = []
                for i in range(sz_1):
                    ln = f.readline().rstrip()
                    if len(ln) > 0:
                        d = list(map(float, ln.split(';')))
                    else:
                        d = []
                    w.append(d)
                self.weights.append(w)

    def save(self, file_name: str):
        f = open(file_name, 'w', encoding='utf-8')
        b = 0
        if self.bias:
            b = 1
        print(self.input_sz, self.output_sz, b, sep=';', file=f)
        print(self.learning_rate, self.lamda, self.dropout, sep=';', file=f)
        print(*self.layers, sep=';', file=f)
        for lay in range(len(self.layers) + 1):
            sz_1 = self.output_sz
            if lay < len(self.layers):
                sz_1 = self.layers[lay]
            for i in range(sz_1):
                print(*self.weights[lay][i], sep=';', file=f)

    def get_neurons(self, input_layer: list, is_learn: bool = False):
        neurons = []
        cur_layer = utils.copy(input_layer)
        if self.bias:
            cur_layer.append(1)
        for i in range(len(self.weights)):
            cur_layer = utils.multiply_matrix_vector(self.weights[i], cur_layer)
            for j in range(len(cur_layer)):
                cur_layer[j] = utils.sigma(cur_layer[j])
            if self.bias and i != len(self.weights) - 1:
                cur_layer.append(1)
            if self.dropout > 0 and i != len(self.weights) - 1 and is_learn:
                for j in range(len(cur_layer)):
                    if random() < self.dropout:
                        cur_layer[j] = 0
            neurons.append(utils.copy(cur_layer))
        return neurons

    def get_output(self, input_layer: list):
        neurons = self.get_neurons(input_layer)
        return neurons[-1]

    def back_propagation(self, input_layer: list, real_output: list):
        neurons = self.get_neurons(input_layer, True)
        self.delta = []
        for i in range(len(self.weights)):
            self.delta.append(0)
        for lay in reversed(range(0, len(self.weights))):
            cur_delta = []
            layer = self.weights[lay]
            errors = []
            if lay != len(self.weights) - 1:
                errors = utils.multiply_matrix_vector_t(self.weights[lay + 1], self.delta[lay + 1])
            else:
                for j in range(len(layer)):
                    errors.append(real_output[j] - neurons[lay][j])
            for j in range(len(layer)):
                cur_delta.append(errors[j] * utils.sigma_dif(neurons[lay][j]))
            self.delta[lay] = cur_delta
        for lay in range(len(self.weights)):
            if lay != 0:
                inputs = neurons[lay - 1]
            else:
                inputs = utils.copy(input_layer)
                if self.bias:
                    inputs.append(1)
            for i in range(len(self.weights[lay])):
                for j in range(len(inputs)):
                    self.weights[lay][i][j] -= self.learning_rate * self.lamda * self.weights[lay][i][j] / self.output_sz
                    self.weights[lay][i][j] += self.learning_rate * self.delta[lay][i] * inputs[j]
