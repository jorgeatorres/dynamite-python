# encoding: utf-8

import math

from dynamite.core import PlanarSystem


class Pendulum2D(PlanarSystem):
    
    def __init__(self):
        super(Pendulum2D, self).__init__()

    def getName(self):
        return 'x\'=-y + cos(2x), y\'=x+sin(2y)'

    def evaluate(self, x, y, t):
        return [-y + math.cos(2*x), x+math.sin(2*y)]
