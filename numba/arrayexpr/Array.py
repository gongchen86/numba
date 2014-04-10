import numpy as np
import operator
from pylab import imshow, show
from alge import Case, of, datatype
from collections import namedtuple


UnaryOperation = datatype('UnaryOperation', ['operand', 'op', 'op_str'])
BinaryOperation = datatype('BinaryOperation', ['lhs', 'rhs', 'op', 'op_str'])
ArrayAssignOperation = datatype('ArrayAssignOperation', ['operand', 'key', 'value'])
ArrayNode = datatype('ArrayNode', ['data', 'operation'])
ScalarConstantNode = datatype('ScalarConstantNodeNode', ['value'])


def unary_op(op, op_str):
    
    def wrapper(func):
        def impl(self):
            return DeferredArray(data=None,
                operation=UnaryOperation(self.array_node, op, op_str))

        return impl

    return wrapper


def binary_op(op, op_str):
    
    def wrapper(func):
        def impl(self, other):
            if isinstance(other, DeferredArray):
                other = other.array_node
            else:
                other = ScalarConstantNode(other)
            return DeferredArray(data=None,
                operation=BinaryOperation(self.array_node, other, op, op_str))

        return impl

    return wrapper


class DeferredArray(object):

    def __init__(self, data=None, operation=None):
        self.array_node = ArrayNode(data=data, operation=operation)

    def __str__(self):
        return str(Value(self.array_node))
    
    @binary_op(operator.add, 'operator.add')
    def __add__(self, other):
        pass

    @binary_op(operator.sub, 'operator.sub')
    def __sub__(self, other):
        pass

    @binary_op(operator.mul, 'operator.mul')
    def __mul__(self, other):
        pass

    @binary_op(operator.div, 'operator.div')
    def __div__(self, other):
        pass

    @binary_op(operator.le, 'operator.le')
    def __le__(self, other):
        pass

    @binary_op(operator.pow, 'operator.pow')
    def __pow__(self, other):
        pass

    @binary_op(operator.getitem, 'operator.getitem')
    def __getitem__(self, other):
        pass

    def __setitem__(self, key, value):
        self.array_node = ArrayNode(data=None,
            operation=ArrayAssignOperation(self.array_node, key, value.array_node))


@unary_op(np.abs, 'abs')
def numba_abs(operand):
    pass


class Value(Case):

    @of('ArrayNode(data, operation)')
    def array(self, data, operation):
        if data is not None:
            return data
        else:
            return Value(operation)

    @of('ScalarConstantNode(value)')
    def scalar_constant(self, value):
        return value

    @of('UnaryOperation(operand, op, op_str)')
    def unary_operation(self, operand, op, op_str):
        return op(Value(operand))

    @of('BinaryOperation(lhs, rhs, op, op_str)')
    def binary_operation(self, lhs, rhs, op, op_str):
        return op(Value(lhs), Value(rhs))

    @of('ArrayAssignOperation(operand, key, value)')
    def array_assign_operation(self, operand, key, value):
        operator.setitem(Value(operand), key, Value(value))
        return Value(operand)


class CodeGen(Case):

    @of('ArrayNode(data, operation)')
    def array(self, data, operation):
        if data is not None:
            self.state['count'] += 1
            return 'x' + str(self.state['count'])
        else:
            return CodeGen(operation, state=self.state)

    @of('ScalarConstantNode(value)')
    def scalar_constant(self, value):
        return str(value)

    @of('UnaryOperation(operand, op, op_str)')
    def unary_operation(self, operand, op, op_str):
        return op_str + '(' +  CodeGen(operand, state=self.state) + ')'

    @of('BinaryOperation(lhs, rhs, op, op_str)')
    def binary_operation(self, lhs, rhs, op, op_str):
        return op_str + '(' + CodeGen(lhs, state=self.state) + ',' + \
            CodeGen(rhs, state=self.state) + ')'


def test1():

    a1 = DeferredArray(data=np.arange(-10,10))
    a2 = DeferredArray(data=np.arange(-10,10))

    result = a1**2 + numba_abs(a2)

    print result
    print CodeGen(result.array_node, state={'count': 0})


def test2():

    a = DeferredArray(data=np.arange(-10,10))

    a[:] = a + a

    print a


def test_mandelbrot():

    width = 900
    height = 600
    x_min = -2.0
    x_max = 1.0
    y_min = -1.0
    y_max = 1.0
    num_iterations = 20

    x, y = np.meshgrid(np.linspace(x_min, x_max, width),
                       np.linspace(y_min, y_max, height))

    c = DeferredArray(data = x + 1j*y)
    #z = c.copy()
    z = DefferedArray(data = x + 1j*y)

    image = DeferredArray(data = np.zeros((height, width)))

    for i in range(num_iterations):

        indices = (np.abs(z) <= 10)
        z[indices] = (z[indices] ** 2) + c[indices]
        image[indices] = i

    imgplot = imshow(np.log(image))
    show()


if __name__ == '__main__':
    test1()
    test2()

