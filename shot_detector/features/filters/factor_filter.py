# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import six

from shot_detector.features.norms import L2Norm

from .base_math_filter import BaseMathFilter


class FactorFilter(BaseMathFilter):

    __logger = logging.getLogger(__name__)

    def filter_feature_item(self, feature, factor=1, dividend=0, offset=0, **kwargs):
        res_features = factor * feature + dividend / self.escape_null(feature) + offset
        return res_features
