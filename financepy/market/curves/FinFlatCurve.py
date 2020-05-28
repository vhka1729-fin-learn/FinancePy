##############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
##############################################################################


import numpy as np

##########################################################################

from ...finutils.FinDate import FinDate
from ...finutils.FinError import FinError
from ...finutils.FinDayCount import FinDayCount
from ...finutils.FinHelperFunctions import inputTime, inputFrequency
from ...market.curves.FinDiscountCurve import FinDiscountCurve
from ...finutils.FinHelperFunctions import labelToString

##########################################################################


class FinFlatCurve(FinDiscountCurve):
    ''' A trivally simple curve based on a single zero rate with its own
    specified compounding method. Hence the curve is assumed to be flat. '''

##########################################################################

    def __init__(self, curveDate, rate, compoundingFreq=-1):
        ''' Create a FinFlatCurve which requires a curve date. '''

        if not isinstance(curveDate, FinDate):
            raise FinError("CurveDate is not a date " + str(curveDate))

        self._curveDate = curveDate
        self._rate = rate
        self._cmpdFreq = inputFrequency(compoundingFreq)

        # Some methods require these members but don't do this if rates is
        # an array of doubles else it will fail due to vectorisations of
        # different lengths

        self._times = None
        self._values = None

        if isinstance(rate, np.ndarray) is False:
            self._times = np.linspace(0.0, 10.0, 40)
            self._values = self.df(self._times)

##########################################################################

    def zeroRate(self, dt, compoundingFreq):
        ''' Return the zero rate which is simply the curve rate. '''

        t = inputTime(dt, self)
        f = inputFrequency(compoundingFreq)

        if f == self._cmpdFreq:
            return self._rate

        if self._cmpdFreq == 0:
            raise FinError("Compounding frequency cannot be zero.")
        elif self._cmpdFreq == -1:
            df = np.exp(-self._rate * t)
        else:
            df = (1.0 + self._rate/self._cmpdFreq)**(-t*self._cmpdFreq)

        if f == 0:  # Simple interest
            r = (1.0/df-1.0)/t
        elif f == -1:  # Continuous
            r = -np.log(df) / t
        else:
            r = (df**(-1.0/t) - 1) * f
        return r

##########################################################################

    def bump(self, bumpSize):
        ''' Calculate the continuous forward rate at the forward date. '''
        r = self._rate + bumpSize
        discCurve = FinFlatCurve(self._curveDate, r,
                                 compoundingFreq=self._cmpdFreq)
        return discCurve

##########################################################################

    def fwd(self, dt):
        ''' Return the fwd rate which is simply the zero rate. '''
        fwdRate = self._rate
        return fwdRate

##########################################################################

    def df(self, dt):
        ''' Return the discount factor based on the compounding approach. '''
        t = inputTime(dt, self)

        f = self._cmpdFreq

        if f == 0:
            raise FinError("Frequency cannot be zero.")
        elif f == -1:
            df = np.exp(-self._rate * t)
        else:
            df = np.power((1.0 + self._rate / f), (-t * f))
        return df

##########################################################################

    def fwdRate(self, date1, date2, dayCountType):
        ''' Calculate the forward rate according to the specified
        day count convention. '''

        if date1 < self._curveDate:
            raise ValueError("Date1 before curve date.")

        if date2 < date1:
            raise ValueError("Date2 must not be before Date1")

        dayCount = FinDayCount(dayCountType)
        yearFrac = dayCount.yearFrac(date1, date2)
        df1 = self.df(date1)
        df2 = self.df(date2)
        fwd = (df1 / df2 - 1.0) / yearFrac
        return fwd

##########################################################################

    def __repr__(self):

        if self._times is None:
            s = "Due to vectorisation issue, this has not been stored."
            return s

        numPoints = len(self._times)
        s = labelToString("TIMES", "DISCOUNT FACTORS")
        for i in range(0, numPoints):
            s += labelToString(self._times[i], self._values[i])

        return s

##########################################################################

    def print(self):
        ''' Simple print function for backward compatibility. '''
        print(self)

##########################################################################
