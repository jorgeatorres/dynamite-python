# encoding: utf-8

import math

class PlanarSystem(object):

    def getName(self):
        return self._label

    def evaluate(self, x, y, t):
        raise NotImplementedError('evaluate()')


# an example PlanarSystem
class Pendulum2D(PlanarSystem):
    
    def __init__(self):
        super(Pendulum2D, self).__init__()

    def getName(self):
        return 'x\'=-y + cos(2x), y\'=x+sin(2y)'

    def evaluate(self, x, y, t):
        return [-y + math.cos(2*x), x+math.sin(2*y)]



class Pendulum2D(PlanarSystem):
    
    def __init__(self):
        super(Pendulum2D, self).__init__()

    def getName(self):
        return 'x\'=-y + cos(2x), y\'=x+sin(2y)'

    def evaluate(self, x, y, t):
        return [-y + math.cos(2*x), x+math.sin(2*y)]
