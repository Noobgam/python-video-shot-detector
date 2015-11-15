# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

import six

import numpy as np

from .base_stat_swfilter import BaseStatSWFilter


class MaxSWFilter(BaseStatSWFilter):

    __logger = logging.getLogger(__name__)

    def aggregate_window_item(self, window_features, **kwargs):
        return self.get_max(window_features, **kwargs)