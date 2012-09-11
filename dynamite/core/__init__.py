# encoding: utf-8

class PlanarSystem(object):

    def evaluate(self, x, y, t):
        raise NotImplementedError('evaluate()')

    def formula(self):
        return u'(Formula Unavailable)'


class ParsedSystem(PlanarSystem):

    def __init__(self, dx, dy):
        self._dx = dx
        self._dy = dy
 
    def evaluate(self, x, y, t):
        subs = {'x': x, 'y': y, 't': t}

        xN, yN = self._dx.simplify(subs), self._dy.simplify(subs)

        if xN._header != 'Number' or yN._header != 'Number':
            raise Exception('Evaluation did not return a number')

        return xN.value(), yN.value()