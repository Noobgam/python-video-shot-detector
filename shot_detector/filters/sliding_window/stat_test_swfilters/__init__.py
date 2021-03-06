# -*- coding: utf8 -*-

"""
    Statistical filters collection based on sliding windows
"""

from __future__ import absolute_import, division, print_function

from .ks_2samp_swfilter import KolmogorovSmirnov2SamplesTestSWFilter
from .normal_test_swfilter import NormalTestSWFilter
from .ranksums_swfilter import WilcoxonRankSumSWFilter
from .stat_test_swfilter import StatTestSWFilter
from .ttest_ind_swfilter import IndependentStudentTtestSWFilter
from .ttest_rel_swfilter import DependentStudentTtestSWFilter
