# encoding: utf-8

import math


class Expr(object):

    def __init__(self, header, args=[]):
        self._header = header
        self._attrs = 0
        self._args = [args] if type(args) != list else args

    def _checkArity(self, arity=1):
        if len(self._args) != arity:
            raise Exception(u'Operator "%s" supports only %d arguments, received %d' % (self._header, arity, len(self._args)))

    def _simplifyArgs(self, subs={}):
        return [x.simplify(subs) for x in self._args]

    def _flatten(self, args):
        newargs = []
        for x in args:
            if x._header == self._header:
                newargs.extend(x._args)
            else:
                newargs.append(x)
        
        return newargs

    def isNumeric(self):
        return self._header == 'Number'

    def isSymbol(self):
        return self._header == 'Symbol'

    def value(self):
        if self.isNumeric() or self.isSymbol():
            return self._args[0]
        else:
            return self._args

    def simplify(self, subs={}):
        if self.isSymbol() and subs and self.value() in subs:
            return Expr(u'Number', subs[self.value()])

        if self._header == '=':
            return self.__class__(self._header, self._simplifyArgs(subs))

        return self

    def hasSymbol(self, symbol, recursive=True):
        if not recursive:
            raise Exception('non recursive search not supported')

        if self.isNumeric():
            return False

        if self.isSymbol():
            if self.value() == symbol:
                return True
            return False

        for x in self._args:
            if x.hasSymbol(symbol):
                return True

        return False

    def __repr__(self):
        return '%s(%s)' % (self._header, self._args)

    def formula(self):
        return u'(Formula Unavailable)'


class Expr_Plus(Expr):
    def __init__(self, args):
        super(Expr_Plus, self).__init__(u'+', args)

    def simplify(self, subs={}):
        args = self._flatten(self._simplifyArgs(subs))

        n = 0.0
        newargs = []

        for x in args:
            if x._header == 'Number':
                n += x.value()
            else:
                newargs.append(x)

        if newargs:
            if n != 0.0:
                return self.__class__([Expr(u'Number', n)] + newargs)
            else:
                return self.__class__(newargs)
        else:
            return Expr(u'Number', n)

    def formula(self):
        return ' + '.join(self._args)


class Expr_Mul(Expr):
    
    def __init__(self, args):
        super(Expr_Mul, self).__init__(u'*', args)

    def simplify(self, subs={}):
        args = self._flatten(self._simplifyArgs(subs))

        n = 1.0
        newargs = []

        for x in args:
            if x._header == 'Number':
                n *= x.value()
            else:
                newargs.append(x)

        if newargs:
            if n != 1.0:
                return self.__class__([Expr(u'Number', n)] + newargs)
            else:
                return self.__class__(newargs)
        else:
            return Expr(u'Number', n)


class Expr_Div(Expr):

    def __init__(self, args):
        super(Expr_Div, self).__init__(u'/', args)
        self._checkArity(2)

    def simplify(self, subs={}):
        arg0, arg1 = self._simplifyArgs(subs)

        if arg1.isNumeric() and arg1.value() == 1.0:
            return arg0.simplify()

        if arg0.isNumeric() and arg0.value() == 0.0:
            return Expr(u'Number', 0.0)

        if arg0.isNumeric() and arg1.isNumeric():
            return Expr(u'Number', arg0.value() / arg1.value())

        # dx/dt and dy/dt are really the symbol dx/dt and dy/dt
        if arg0.isSymbol() and arg1.isSymbol() and (arg0.value() == 'dx' or arg0.value() == 'dy') and arg1.value() == 'dt':
            return Expr(u'Symbol', u'%s/%s' % (arg0.value(), arg1.value()))

        return self


class Expr_List(Expr):

    def __init__(self, args=[]):
        super(Expr_List, self).__init__(u'List', args)

    def simplify(self, subs={}):
        args = self._simplifyArgs(subs)
        return Expr_List(args)

    def formula(self):
        f = u'{'

        for x in self._args:
            f += x.formula() + ','

        f = f[:-1]
        f += u'}'

        return f


class Expr_NumericFunction(Expr):

    ALLOWED_FUNCTIONS = {
        'sin': math.sin,    
        'cos': math.cos
    }

    def __init__(self, fname, arg):
        super(Expr_NumericFunction, self).__init__(u'NumericFunction', [arg])
        
        if fname not in Expr_NumericFunction.ALLOWED_FUNCTIONS:
            raise Exception(u'Function "%s" is unknown' % fname)

        self._checkArity(1) 

        self._fname = fname

    def simplify(self, subs={}):
        arg0, = self._simplifyArgs(subs)

        if arg0.isNumeric():
            return Expr(u'Number', Expr_NumericFunction.ALLOWED_FUNCTIONS[self._fname](arg0.value()))

        return self

    def __repr__(self):
        return '%s(%s)' % (self._fname, self._args)