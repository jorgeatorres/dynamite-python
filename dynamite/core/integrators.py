# encoding: utf-8

from PySide.QtCore import QPointF


class RungeKutta4(object):

    @classmethod
    def solve(cls, system, x0, y0, t0, steps=20):
        H = 0.05
        sol = []

        xp = QPointF(x0, y0)
        sol.append(xp)

        xval = x0
        yval = y0
        tval = t0

        for n in xrange(0, steps):
            L1, M1 = system.evaluate(xval, yval, tval)
            
            x1 = xval + H*L1/2;
            y1 = yval + H*M1/2;
            t1 = tval + H/2;

            L2, M2 = system.evaluate(x1, y1, t1)
            x1 = xval + H*L2/2;
            y1 = yval + H*M2/2;

            L3, M3 = system.evaluate(x1, y1, t1)

            x1 = xval + H*L3;
            y1 = yval + H*M3;
            tval = tval + H;

            L4, M4 = system.evaluate(x1, y1, tval)

            xval = xval + H*(L1+2*L2+2*L3+L4)/6;
            yval = yval + H*(M1+2*M2+2*M3+M4)/6;

            sol.append(QPointF(xval, yval))
    
        return sol
