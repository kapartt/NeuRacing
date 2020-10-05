import math


def sigma(x: float) -> float:
    if x < -100:
        return 0.0
    if x > 100:
        return 1.0
    return 1 / (1 + math.exp(-x))


def sigma_dif(func_val: float) -> float:
    return func_val * (1 - func_val)


def multiply_matrix_vector(m: list, v: list):
    if len(m) == 0:
        return None
    if len(m[0]) != len(v):
        return None
    res = []
    for i in range(len(m)):
        s = 0
        for j in range(len(v)):
            s += m[i][j] * v[j]
        res.append(s)
    return res


def multiply_matrix_vector_t(m: list, v: list):
    if len(m) != len(v):
        return None
    if len(m) == 0:
        return None
    res = []
    for j in range(len(m[0])):
        s = 0
        for i in range(len(v)):
            s += m[i][j] * v[i]
        res.append(s)
    return res


def copy(a: list) -> list:
    b = []
    for x in a:
        b.append(x)
    return b


def error(a: list, b: list) -> float:
    s = 0
    for i in range(len(a)):
        s += (a[i] - b[i]) ** 2
    return math.sqrt(s) / len(a)
