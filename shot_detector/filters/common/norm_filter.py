# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function, \
    unicode_literals

import logging

from shot_detector.features.norms import L1Norm
from shot_detector.features.norms import L2Norm
from shot_detector.filters.dsl import DslPlainFilter


class NormFilter(DslPlainFilter):
    """
        ...
    """
    __logger = logging.getLogger(__name__)

    @DslPlainFilter.dsl_kwargs_decorator(
        ('norm_function', (int, str),
         ['l', 'nm', 'norm', 'f', 'fun', 'function']),
    )
    def filter_feature_item(self,
                            feature,
                            norm_function=None,
                            **kwargs):
        """
        
        :param feature: 
        :param norm_function: 
        :param kwargs: 
        :return: 
        """

        if 1 == norm_function or 'l1' == norm_function:
            norm_function = L1Norm.length
        elif 2 == norm_function or 'l2' == norm_function:
            norm_function = L2Norm.length
        else:
            norm_function = L1Norm.length
        return norm_function(feature, **kwargs)
