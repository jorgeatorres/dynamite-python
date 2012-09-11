# encoding: utf-8

import StringIO
import token, tokenize

from dynamite.parser import expressions as expr


class ParserException(Exception):
    pass


class Token(object):
    UNKNOWN = 0

    NUMBER = u'number'
    NAME = u'name'
    PLUS = u'+'
    MINUS = u'-'
    MUL = u'*'
    DIV = u'/'
    EXP = u'^'
    LPAR = u'('
    RPAR = u')'
    LBRACE = u'{'
    RBRACE = u'}'
    EQUAL = u'='
    COMMA = u','
    END = u'(end)'

    _OP_BINDING = {
        LBRACE: 5,
        EQUAL: 5,
        PLUS: 50,
        MINUS: 50,
        MUL: 60,
        DIV: 60
    }

    def __init__(self, kind=0, value=''):
        self.kind = kind
        self.value = value

    def isNumber(self):
        return self.kind == Token.NUMBER

    def isName(self):
        return self.kind == Token.NAME

    def isOperator(self):
        return self.kind in (Token.PLUS, Token.MINUS, Token.MUL, Token.DIV, Token.EXP, Token.EQUAL)

    @property
    def lbp(self):
        return Token._OP_BINDING.get(self.kind, 0)

    def __repr__(self):
        return u'<%s: %s>' % (self.kind, self.value)


# The parser is a simple top-down parser based on http://javascript.crockford.com/tdop/tdop.html
# from Douglas Crockford (http://www.crockford.com/)

class ExpressionParser(object):

    def __init__(self, *args, **kwargs):
        self._tokens = None
        self._pos = -1

    # Token-related
    @classmethod
    def tokenize(cls, text):
        # token_pat = re.compile("\s*(?:(\d+)|(.))")

        tokens = []

        for toknum, tokval, _, _, _ in tokenize.generate_tokens(StringIO.StringIO(text).readline):
            type_ = Token.UNKNOWN

            if token.ISEOF(toknum):
                type_ = Token.END
            else:
                if toknum == token.NUMBER:
                    type_ = Token.NUMBER
                elif toknum == token.NAME:
                    type_ = Token.NAME
                elif toknum == token.OP:
                    # python uses token.OP both for delimiters and operators, so we need to know more
                    if tokval == '+':
                        type_ = Token.PLUS
                    elif tokval == '-':
                        type_ = Token.MINUS
                    elif tokval == '*':
                        type_ = Token.MUL
                    elif tokval == '/':
                        type_ = Token.DIV
                    elif tokval == '^':
                        type_ = Token.EXP
                    elif tokval == '(':
                        type_ = Token.LPAR
                    elif tokval == ')':
                        type_ = Token.RPAR
                    elif tokval == '{':
                        type_ = Token.LBRACE
                    elif tokval == '}':
                        type_ = Token.RBRACE
                    elif tokval == '=':
                        type_ = Token.EQUAL
                    elif tokval == ',':
                        type_ = Token.COMMA
                elif toknum == token.EQUAL:
                    type_ = Token.EQUAL

            tokens.append(Token(type_, tokval))

        return tokens

    def _token(self):
        return self._tokens[self._pos]

    def _prevToken(self):
        if 0 > self._pos:
            self._pos -= 1
            return self._token()

        raise Exception(u'No previous token')

    def _nextToken(self, expectedToken=None):
        if expectedToken is not None and self._token().kind != expectedToken:
            raise Exception(u'Expected %s' % expectedToken)

        if self._pos < (len(self._tokens) - 1):
            self._pos += 1
            return self._token()

        raise Exception(u'No next token')

    def _peekToken(self):
        if self._pos < (len(self._tokens) - 1):
            return self._tokens[self._pos + 1]
        return None


    # Parsing
    def parse(self, text):
        self._pos = -1
        self._tokens = ExpressionParser.tokenize(text)

        self._nextToken()
        return self._expression()

    def _nud(self, token):
        if token.isNumber():
            return expr.Expr(u'Number', float(token.value))
        elif token.isName():
            if self._token().kind == Token.LPAR:
                # we only support numeric functions of 1 argument
                self._nextToken()
                e = expr.Expr_NumericFunction(token.value, self._expression(0))
                self._nextToken()
                return e

            return expr.Expr(u'Symbol', unicode(token.value))
        elif token.kind == Token.LBRACE:
            parts = []

            if self._token().kind != Token.RBRACE:
                while True:
                    if self._token().kind == Token.RBRACE:
                        break

                    parts.append(self._expression(0))

                    if self._token().kind != Token.COMMA:
                        break
                    self._nextToken(Token.COMMA)

                    # if self._token().kind != Token.COMMA:
                    #     parts.append(self._expression(0))

                self._nextToken(Token.RBRACE)

            return expr.Expr_List(parts)
        elif token.kind == Token.MINUS:
            return expr.Expr_Mul([expr.Expr(u'Number', -1.0), self._expression(100)]) # unary version
        elif token.kind == Token.LPAR:
            e = self._expression(0)
            self._nextToken(Token.RPAR)
            return e

        return None


    def _led(self, token, l):
        if token.isOperator():
            if token.kind == Token.PLUS:
                return expr.Expr_Plus([l, self._expression(token.lbp)])
            elif token.kind == Token.MINUS:
                return expr.Expr_Plus([l, expr.Expr_Mul([ expr.Expr(u'Number', -1.0), self._expression(token.lbp)]) ])
            elif token.kind == Token.MUL:
                return expr.Expr_Mul([l, self._expression(token.lbp)])
            elif token.kind == Token.DIV:
                return expr.Expr_Div([l, self._expression(token.lbp)])
            return expr.Expr(token.kind, [l, self._expression(token.lbp)])

        return None

    def _expression(self, rbp=0):
        t = self._token()
        self._nextToken()        
        expr = self._nud(t)

        while rbp < self._token().lbp:
            t = self._token()
            self._nextToken()
            expr = self._led(t, expr)

        return expr

    # def _expect(self, ttype):
    #     if self._token()[0] != ttype:
    #         raise Exception('Expected "%s"' % c)
    #     self._nextToken()


    # def _processToken(self):
    #     ttype, token = self._token()

    #     if ttype == Token.NUMBER:
    #         expr = Expression('Number', token)
    #         self._nextToken()
    #         return expr
    #     elif ttype == Token.NAME:
    #         if self._peekToken()[0] == Token.LPAR:
    #             self._nextToken()
    #             self._expect(Token.LPAR)
                
    #             enclosed = self._expression(0)
    #             self._expect(Token.RPAR)

    #             return Expression(Expression('Symbol', token), enclosed)
    #         else:
    #         # TODO: distinguish between function calls and symbols
    #             # if (procs [i].equals (tokens.sval)) {
    #             #   next ();
    #             #   expect ('(');
    #             #   Expr rand = parse_expr (0);
    #             #   expect (')');
    #             #   return Expr.make_app1 (rators [i], rand);
    #             # }            

    #             expr = Expression('Symbol', token)
    #             self._nextToken()
    #             return expr
    #     elif ttype == Token.LPAR:
    #         self._nextToken()

    #         enclosedExpr = self._expression(0)
    #         self._expect(Token.RPAR)

    #         return enclosedExpr
    #     elif ttype == Token.MINUS:
    #         self._nextToken()
    #         return Expression('Neg', self._expression(15))
    #     else:
    #         raise Exception('expected a factor')


def parse(text):
    return ExpressionParser().parse(text)

# TODO: this really belongs somewhere else
def convert(expression):
    from PySide.QtCore import QPointF
    from dynamite.core import ParsedSystem
    from dynamite.plots.diffeq import OrbitPlot

    e = expression.simplify()

    if e._header == 'List':
        if e.hasSymbol('dy/dt') and e.hasSymbol('dx/dt'):
            parts = {'dy/dt': None, 'dx/dt': None, 'x0': None, 'y0': None}

            for x in e._args:
                if x._header == '=':
                    if x._args[0].isSymbol() and x._args[0].value() == 'dy/dt':
                        parts['dy/dt'] = x._args[1]
                    elif x._args[0].isSymbol() and x._args[0].value() == 'dx/dt':
                        parts['dx/dt'] = x._args[1]
                    elif x._args[0].isSymbol() and (x._args[0].value() == 'x_0' or x._args[0].value() == 'x0'):
                        parts['x0'] = x._args[1].value()
                    elif x._args[0].isSymbol() and (x._args[0].value() == 'y_0' or x._args[0].value() == 'y0'):
                        parts['y0'] = x._args[1].value()

            if None not in parts.values():
                system = ParsedSystem(parts['dx/dt'], parts['dy/dt'])
                plot = OrbitPlot(system, QPointF(parts['x0'], parts['y0']))
                plot._formula = expression.formula()
                return plot
            else:
                if parts['dy/dt'] is not None and parts['dx/dt'] is not None:
                    pass
                    #system2d
    else:
        return e.value()

    return None