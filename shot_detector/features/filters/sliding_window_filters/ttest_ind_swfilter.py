# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from .scipy_stat_swfilter import SciPyStatSWFilter



class TTestIndSWFilter(SciPyStatSWFilter):
    """
    Calculates the T-test for the means of TWO INDEPENDENT samples of scores.

    This is a two-sided test for the null hypothesis
    that 2 independent samples have identical
    average (expected) values.
    This test assumes that the populations
    have identical variances by default.

    """

    __logger = logging.getLogger(__name__)

    def aggregate_windows(self,
                          window_seq,
                          depth=0,
                          **kwargs):

        prev_win = None
        for window in window_seq:
            if prev_win is None:
                prev_win = window

            result = self.ttest_ind(prev_win, window, equal_var=False)
            print (result)

            yield 1 - result.pvalue
            prev_win = window
