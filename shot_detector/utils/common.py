# -*- coding: utf8 -*-
"""
    This is part of shot detector.
    Produced by w495 at 2017.05.04 04:18:27
"""

from __future__ import absolute_import, division, print_function

import collections
import inspect
import os
import os.path
from bisect import bisect_left

import scipy.misc
import six

if six.PY3:
    # noinspection PyUnusedLocal
    def uni(s, *args, **kwargs):
        """
        
        :param s: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        return s

else:
    # noinspection PyUnusedLocal
    def uni(s, *args, **kwargs):
        """
        
        :param s: 
        :param args: 
        :param kwargs: 
        :return: 
        """
        # noinspection PyUnresolvedReferences
        return unicode(s, "utf8")


def yes_no(arg=None):
    """
    
    :param arg: 
    :return: 
    """
    choices = {
        True: ('yes', 'y', 'true', 't', '1'),
        False: ('no', 'n', 'false', 'f', '0')
    }

    if not arg:
        arg = 'no'
    arg = str(arg)
    arg = arg.lower()
    if arg in choices[True]:
        return True
    if arg in choices[False]:
        return False
    return False


def car(lst):
    """
    
    :param lst: 
    :return: 
    """
    return (lst or [None])[0]


def unique_hashable(a):
    """
    
    :param a: 
    :return: 
    """
    return tuple(iter_unique_hashable(a))


def iter_unique_hashable(a):
    """
    
    :param a: 
    :return: 
    """
    seen = set()
    return (seen.add(x) or x for x in a if x not in seen)


def unique(seq):
    """
        Remove duplicates. Preserve order first seen.
        Assume orderable, but not hashable elements
    """
    return tuple(iter_unique(seq))


def iter_unique(seq):
    """
        Remove duplicates. Preserve order first seen.
        Assume orderable, but not hashable elements
    """
    seen = []
    for item in seq:
        index = bisect_left(seen, item)
        if index == len(seen) or seen[index] != item:
            seen.insert(index, item)
            yield item


def is_whole(x):
    """
    
    :param x: 
    :return: 
    """
    if x % 1 == 0:
        return True
    else:
        return False


def is_instance(obj):
    """
    
    :param obj: 
    :return: 
    """
    if not hasattr(obj, '__dict__'):
        return False
    if inspect.isroutine(obj):
        return False
    if inspect.isclass(obj):
        # class type
        return False
    else:
        return True


def get_objdata_dict(obj, ext_classes_keys=None):
    """
    
    :param obj: 
    :param ext_classes_keys: 
    :return: 
    """
    if ext_classes_keys is None:
        ext_classes_keys = []
    res = []
    for key, val in inspect.getmembers(
            obj,
            predicate=lambda x: not inspect.isroutine(x)
    ):
        if not key.startswith('__'):
            if key in ext_classes_keys:
                try:
                    val_dict = get_objdata_dict(val, ext_classes_keys)
                    res += [(key, val_dict)]
                except ValueError:
                    res += [(key, str(val))]
            elif type(val) in (tuple, list):
                val_list = list(val)
                rval_list = []
                for i, xval in enumerate(val_list):
                    nval = get_objdata_dict(xval, ext_classes_keys)
                    rval_list += [(str(i), nval)]
                key = "%s (%s)" % (key, len(rval_list))
                # noinspection PyArgumentList
                res += [(key, collections.OrderedDict(rval_list))]
            else:
                res += [(key, val)]
    # noinspection PyArgumentList
    return collections.OrderedDict(res)


# noinspection PyUnusedLocal
def save_features_as_image(features, number, subdir='filter',
                           priv='priv', prefix='image', **_kwargs):
    """

    cat *.jpg | ffmpeg -f image2pipe  -s 16x16  
        -pix_fmt yuv420p  -c:v mjpeg -i - -vcodec libx264 out.mp4


    :param features:
    :param number:
    :param subdir:
    :param priv:
    :param prefix:
    :return:
    """
    path = '%s/%s' % (priv, subdir)
    if isinstance(features, collections.Iterable):
        if not os.path.exists(path):
            os.makedirs(path)
        # noinspection PyTypeChecker
        scipy.misc.imsave(
            '%s/%s-%.10d.jpg' %
            (path, prefix, number),
            features
        )
