# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function

import itertools
import logging
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

__logger = logging.getLogger(__name__)


def handle_content(iterable,
                   unpack=None,
                   handle=None,
                   pack=None,
                   **kwargs):
    """
    Handle each item of iterable in pipeline (!) like this:
        content         = unpack_item(item)
        handled_content = handle_item(content)
        item            = pack_item(item, handled_content)

    :param iterable: some sequence
    :param unpack:
    :param handle:
    :param pack:
    :param kwargs:  additional named arguments, 
        that passes to all of (unpack, handle, pack)
    :return: new iterable with handled content in each item

    Steps of pipeline represented by functions
        unpack: function(iterable, *args, **kwargs) or None
        handle: function(iterable, *args, **kwargs) or None
        pack:   function(iterable, iterable, *args, **kwargs) or None

    If one of the functions is None, 
    this step of pipeline will be skipped.

    So the main scheme of handling:
        content_iterable = unpack(orig_iterable)
        handled_iterable = handle(content)
        result_iterable  = pack_item(orig_iterable, handled_iterable)

    Example:
        >>> def get(iterable):
        ...     for item in iterable:
        ...         yield item.get('value', 0)
        >>>
        >>> def fun(iterable):
        ...     for item in iterable:
        ...         yield item * 2
        >>>
        >>> def set_(iterable, values):
        ...     # zip = itertools.izip
        ...     for item, value in zip(iterable, values):
        ...         item['value'] = value
        ...         yield item
        >>>
        >>> data = [
        ...     dict(name='x', value='1'), 
        ...     dict(name='y', value='2')
        ... ]
        >>>
        >>> list(handle_content(data, get, fun, set_))
        [{'name': 'x', 'value': '2'}, {'name': 'y', 'value': '4'}]
        >>>
    """

    if unpack is None:
        unpack = __default_unpack
    if handle is None:
        handle = __default_handle
    if pack is None:
        pack = __default_pack

    iterable = iter(iterable)
    items, orig_items = itertools.tee(iterable)
    contents = unpack(items, **kwargs)
    handled_contents = handle(contents, **kwargs)
    packed = pack(orig_items, handled_contents, **kwargs)
    return packed


# noinspection PyUnusedLocal
def __default_unpack(items, **_kw):
    return items


# noinspection PyUnusedLocal
def __default_handle(contents, **_):
    """
    
    :param contents: 
    :return: 
    """
    return contents


# noinspection PyUnusedLocal
def __default_pack(orig_items, handled_contents, **_):
    """
    
    :param orig_items: 
    :param handled_contents: 
    :return: 
    """
    return handled_contents


# noinspection PyPep8
def handle_content_parallel(obj_seq, *args, **kwargs):
    """
    
    :param obj_seq: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    future_seq = obj_group_future_seq(
        obj_seq,
        *args,
        **kwargs
    )
    index_group_seq = future_result_seq(future_seq)
    for _, group in sorted(index_group_seq):
        for obj in group:
            yield obj


def future_result_seq(future_seq):
    """
    
    :param future_seq: 
    :return: 
    """
    future_seq = as_completed(list(future_seq))
    for future in future_seq:
        yield future.result()


def obj_group_future_seq(obj_seq, *args, **kwargs):
    """
    
    :param obj_seq: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    chunk_size = kwargs.get('chunk_size')
    pool_size = kwargs.get('pool_size', mp.cpu_count())
    obj_group_seq = group_seq(obj_seq, chunk_size)
    with ProcessPoolExecutor(pool_size) as executor:
        for index, group in enumerate(obj_group_seq):
            # Serialization for submit to ProcessPoolExecutor.
            obj_list = list(group)
            future = executor.submit(
                local_handle_content_parallel,
                index,
                obj_list,
                *args,
                **kwargs
            )
            yield future


def local_handle_content_parallel(index, obj_list, *args, **kwargs):
    """
    
    :param index: 
    :param obj_list: 
    :param args: 
    :param kwargs: 
    :return: 
    """
    obj_seq = iter(obj_list)
    obj_seq = handle_content(
        obj_seq,
        *args,
        **kwargs
    )
    obj_list = list(obj_seq)
    return index, obj_list


def group_seq(iterable, chunk_size=None):
    """
    
    :param iterable: 
    :param chunk_size: 
    :return: 
    """
    if not chunk_size:
        chunk_size = 256
    it = iter(iterable)
    group = list(itertools.islice(it, chunk_size))
    while group:
        yield group
        group = list(itertools.islice(it, chunk_size))
