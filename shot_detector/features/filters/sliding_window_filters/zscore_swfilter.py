# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

import six

import numpy as np

from .base_combination_swfilter import BaseCombinationSWFilter
from .base_stat_swfilter import BaseStatSWFilter


class ZScoreSWFilter(BaseStatSWFilter, BaseCombinationSWFilter):

    __logger = logging.getLogger(__name__)

    def aggregate_window(self, window_features, window_state, *args, **kwargs):
        mean = self.get_mean(window_features)
        std = self.get_std(window_features, mean)
        return (mean, std), window_state

    def combination(self, original_features, aggregated_features, sigma_num, *args, **kwargs):
        mean, std = aggregated_features
        # print (mean, std)
        if self.bool(std == 0, *args, **kwargs):
            return sigma_num
        z_score = abs(original_features - mean) / self.escape_null(std)
        return z_score