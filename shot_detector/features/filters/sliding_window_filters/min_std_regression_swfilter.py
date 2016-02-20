# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

import functools

from collections import namedtuple

from .stat_swfilter import StatSWFilter


class MinStdRegressionSWFilter(StatSWFilter):

    __logger = logging.getLogger(__name__)

    class Atom(object):

        def __init__(self, index, value, state):
            self.index = index
            self.value = value
            self.state = state

    def aggregate_windows(self,
                          window_seq,
                          depth=0,
                          **kwargs):

        for window in window_seq:
            x_window = self.split(window, depth=depth, **kwargs)
            for index, item in enumerate(x_window):
                yield item

                # if index == 0:
                #     yield -0.1
                # else:
                #     yield item

    def split(self, sequence, **kwargs):
        indexed_window = list(
            self.Atom(
                index=index,
                value=value,
                state=False
            )
            for index, value in enumerate(sequence)
        )
        indexed_window = self.split_rec(indexed_window, **kwargs)
        values = list(self.extract_values(indexed_window))
        return values

    def split_rec(self, sequence, depth=0, **kwargs):
        pivot = self.pivot(sequence, **kwargs)
        if depth > 0:
            upper_split = self.filter_part(
                lambda item:
                    item.value >= pivot,
                sequence,
                depth=depth - 1,
                replacer=pivot,
                **kwargs
            )
            lower_split = self.filter_part(
                lambda item:
                    item.value < pivot,
                sequence,
                depth=depth - 1,
                replacer=pivot,
                **kwargs
            )
            sequence = sorted(
                lower_split + upper_split,
                key=lambda item:
                    item.index
            )
        else:
            sequence = list(
                self.replace_items(
                    sequence,
                    replacer=pivot,
                    **kwargs
                )
            )
        return sequence

    def filter_part(self,
                    function_or_none,
                    sequence,
                    replacer=None,
                    **kwargs):
        part = filter(function_or_none, sequence)
        if not part:
            return part
        part_split = self.split_rec(part, **kwargs)
        part_split = list(
            self.replace_items(
                part_split,
                replacer=replacer,
                **kwargs
            )
        )
        return part_split

    def extract_values(self, sequence, **kwargs):
        for item in sequence:
            yield item.value

    def replace_items(self, sequence, replacer=None, **kwargs):
        for item in sequence:
            if not item.state:
                yield self.Atom(
                    index=item.index,
                    value=replacer,
                    state=True
                )
            else:
                yield item

    def pivot(self, sequence, **kwargs):
        values = list(self.extract_values(sequence))
        mean = self.get_mean(list(values), **kwargs)
        return mean



