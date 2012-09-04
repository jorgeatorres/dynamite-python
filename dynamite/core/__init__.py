# encoding: utf-8

class Rectangle(object):
    pass


class Equation(object):
    def evaluate(self, subs):
        return None


class PlanarSystem(object):

    def getName(self):
        return self._label

    def evaluate(self, x, y, t):
        raise NotImplementedError('evaluate()')


class ParsedSystem(PlanarSystem):

    def __init__(self, dx, dy):
        self._label = 'x\' = %s, y\' = %s' % (dx, dy)

        self._dx = dx
        self._dy = dy
 
    def evaluate(self, x, y, t):
        return (self._dx.evalf(5, subs={'x': x, 'y': y, 't': t}), self._dy.evalf(5, subs={'x': x, 'y': y, 't': t}))