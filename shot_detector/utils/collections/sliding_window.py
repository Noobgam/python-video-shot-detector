# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import collections
import types
import itertools


class SlidingWindow(collections.deque):

    DEFAULT_WINDOW_SIZE = 2

    @classmethod
    def sliding_windows(cls, sequence, window_size=None, overlap_size=None, yield_tail=None, strict_windows=None):
        """
        Generates a sequence of sliding windows over the `sequence` (second) parameter.
        It expects that sequence is `iterable` and returns a `generator object`.
        By default the size of the each window is 2,
        but you can specify it with `window_size` (third) parameter.
        Each window implements `collections.deque` interface.

        How can you use it?
        Let define initial sequence and function for uncovering generator content to tuple list.

            >>> sequence = xrange(8)
            >>>
            >>> tuple(sequence)
            (0, 1, 2, 3, 4, 5, 6, 7)
            >>>
            >>> def sliding_windows(*args, **kwargs):
            ...     return list(tuple(sw) for sw in SlidingWindow.sliding_windows(*args, **kwargs))
            ...
            >>>

        Default behaviour: Number of input itens equals to number of output ones.
        This is not right sliding windows, but it is very usefull for many applications.

            >>> default = sliding_windows(sequence, 2)
            >>> default
            [(0,), (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
            >>>
            >>> len(sequence) == len(default)
            True
            >>>
            >>> soft_sw_list_2 = sliding_windows(sequence, window_size=2)
            >>> soft_sw_list_2
            [(0,), (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
            >>>
            >>> len(sequence) == len(soft_sw_list_2)
            True
            >>>
            >>> soft_sw_list_3 = sliding_windows(sequence, window_size=3)
            >>> soft_sw_list_3
            [(0,), (0, 1), (0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), (5, 6, 7)]
            >>>
            >>> len(sequence) == len(soft_sw_list_3)
            True
            >>>
            >>> soft_sw_list_4 = sliding_windows(sequence, window_size=4)
            >>> soft_sw_list_4
            [(0,), (0, 1), (0, 1, 2), (0, 1, 2, 3), (1, 2, 3, 4), (2, 3, 4, 5), (3, 4, 5, 6), (4, 5, 6, 7)]
            >>>
            >>> len(sequence) == len(soft_sw_list_4)
            True
            >>>

        It implements more accurate behaviour with `strict_windows` parametr.

            >>> strict_sw_list_2 = sliding_windows(
            ...     sequence,
            ...     window_size=2,
            ...     strict_windows=True
            ... )
            ...
            >>> strict_sw_list_2
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)]
            >>>
            >>> len(sequence)
            8
            >>> len(strict_sw_list_2)
            7
            >>>
            >>> strict_sw_list_3 = sliding_windows(
            ...     sequence,
            ...     window_size=3,
            ...     strict_windows=True
            ... )
            >>> strict_sw_list_3
            [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), (5, 6, 7)]
            >>>
            >>> len(sequence)
            8
            >>> len(strict_sw_list_3)
            6
            >>>
            >>> strict_sw_list_4 = sliding_windows(
            ...     sequence,
            ...     window_size=4,
            ...     strict_windows=True
            ... )
            >>> strict_sw_list_4
            [(0, 1, 2, 3), (1, 2, 3, 4), (2, 3, 4, 5), (3, 4, 5, 6), (4, 5, 6, 7)]
            >>>
            >>> len(sequence)
            8
            >>> len(strict_sw_list_4)
            5
            >>>

        Also you can overlap windows.
        By default windows overlapped with (window_size - 1) elements.

            >>> strict_lapped_default = sliding_windows(
            ...     sequence,
            ...     window_size=3,
            ...     strict_windows=True
            ... )
            ...
            >>> strict_lapped_default
            [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), (5, 6, 7)]
            >>>
            >>> strict_lapped_3_2 = sliding_windows(
            ...     sequence,
            ...     window_size=3,
            ...     overlap_size=2,
            ...     strict_windows=True
            ... )
            ...
            >>> strict_lapped_3_2
            [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), (5, 6, 7)]
            >>>
            >>> strict_lapped_3_1 = sliding_windows(
            ...     sequence,
            ...     window_size=3,
            ...     overlap_size=1,
            ...     strict_windows=True
            ... )
            ...
            >>> strict_lapped_3_1
            [(0, 1, 2), (2, 3, 4), (4, 5, 6)]
            >>>

        The same you can do with «soft» sliding windows.
        Note that overlapping do not work on the incomplete windows
        (at the start of window sequence).

            >>> soft_lapped_3_1 = sliding_windows(
            ...     sequence,
            ...     window_size=3,
            ...     overlap_size=1,
            ...     strict_windows=False
            ... )
            ...
            >>> soft_lapped_3_1
            [(0,), (0, 1), (0, 1, 2), (2, 3, 4), (4, 5, 6)]
            >>>

        Look at the end of the `soft_lapped_3_1`. There is no `7`.
        It has happened because 7 — the last member of initial sequence
        and it do not fit with overlapping scheme.
        For this case you can use `yield_tail` parameter.

            >>> strict_lapped_3_1_tail = sliding_windows(
            ...     sequence,
            ...     window_size=3,
            ...     overlap_size=1,
            ...     yield_tail=True,
            ...     strict_windows=True
            ... )
            ...
            >>> strict_lapped_3_1_tail
            [(0, 1, 2), (2, 3, 4), (4, 5, 6), (5, 6, 7)]
            >>>

        The same you can do with «soft» sliding windows.

            >>> strict_lapped_3_1_tail = sliding_windows(
            ...     sequence,
            ...     window_size=3,
            ...     overlap_size=1,
            ...     yield_tail=True,
            ...     strict_windows=False
            ... )
            ...
            >>> strict_lapped_3_1_tail
            [(0,), (0, 1), (0, 1, 2), (2, 3, 4), (4, 5, 6), (5, 6, 7)]
            >>>

        It is quite difficult to understand the logic of the last example looking only on the result.
        This is not recommended case of use.

        If you set `overlap_size` greater than `window_size` you will achive some interesting effects

            >>> sliding_windows(sequence, window_size=3, overlap_size=0, strict_windows=True)
            >>>

        For fool-tolerance you cannot set `window_size` and `overlap_size` to the same number,
        because it doesn't make sense.

            >>> sliding_windows(sequence, window_size=3, overlap_size=3)
            Traceback (most recent call last):
                ...
            AssertionError: it does not make sense: overlap each window with `window_size`
            >>>

        In this case you should get:
            [(0,), (0, 1), (0, 1, 2), (0, 1, 2), (0, 1, 2), (0, 1, 2), ... an infinite number of times ... ]
        You can achieve this much more simpler without sliding windows =).
        Also you cannot set window_size less then null:

            >>> sliding_windows(sequence, window_size=0)
            ...
            Traceback (most recent call last):
                ...
            AssertionError: it does not make sense: window with zero size
            >>>

        Also it controls types of arguments:

            >>> sliding_windows(42)
            Traceback (most recent call last):
                ...
            AssertionError: sequence is iterable
            >>>
            >>> sliding_windows(sequence, 2.1)
            Traceback (most recent call last):
                ...
            AssertionError: window_size is positive integer or None (for default)
            >>>
            >>> sliding_windows(sequence, 2, 1.1)
            Traceback (most recent call last):
                ...
            AssertionError: overlap_size is integer or None (for default)
            >>>
            >>> sliding_windows(sequence, 2, yield_tail=0)
            Traceback (most recent call last):
                ...
            AssertionError: yield_tail is boolean or None (for default)
            >>>
            >>> sliding_windows(sequence, 2, strict_windows=0)
            Traceback (most recent call last):
                ...
            AssertionError: strict_windows is boolean or None (for default)
            >>>

        Remember: these assertion errors will not work with pythin optimisation.

        To sum up all examples, this is formal specification.

            :param collections.Iterable sequence:
                initial sequence of any element.
            :param integer window_size:
                size of each sliding window
            :param integer overlap_size: number
            :param boolean yield_tail:
            :param boolean strict_windows:

            :returns: <generator object sliding_windows at ... >
                Do not forget about it. If you want to use the result of this functions several times
                you should apply itertools.tee or convert this generator to concrete objects.

        """
        assert isinstance(sequence, collections.Iterable), \
            'sequence is iterable'
        assert isinstance(window_size, (int, long, types.NoneType)), \
            'window_size is positive integer or None (for default)'
        assert isinstance(overlap_size, (int, long, types.NoneType)), \
            'overlap_size is integer or None (for default)'
        assert isinstance(yield_tail, (bool, types.NoneType)), \
            'yield_tail is boolean or None (for default)'
        assert isinstance(strict_windows, (bool, types.NoneType)), \
            'strict_windows is boolean or None (for default)'

        assert window_size > 0, \
            'it does not make sense: window with zero size'
        assert overlap_size != window_size, \
            'it does not make sense: overlap each window with `window_size`'

        if window_size is None:
            window_size = cls.DEFAULT_WINDOW_SIZE

        if overlap_size is None:
            overlap_size = window_size - 1

        win = SlidingWindow([], maxlen=window_size)
        append = win.append
        yield_condition = None
        for index, item in enumerate(sequence):
            append(item)
            shift = window_size - overlap_size
            yield_condition = (index <= (window_size - 1) or not index % shift)
            if strict_windows:
                yield_condition = (index >= (window_size - 1) and not index % shift)
            if yield_condition:
                yield win
        else:
            if yield_tail and not yield_condition:
                yield win

    def __getitem__(self, index):
        if isinstance(index, slice):
            return type(self)(itertools.islice(self, index.start, index.stop, index.step))
        return super(SlidingWindow, self).__getitem__(index)

