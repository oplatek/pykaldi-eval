#!/usr/bin/env python
# vim: set fileencoding=utf-8
# This code is PEP8-compliant. See http://www.python.org/dev/peps/pep-0008.

from __future__ import unicode_literals

import codecs
from itertools import islice


def load_wavaskey(fname, constructor, limit=None, encoding='UTF-8'):
    """
    Loads a dictionary of objects stored in the "wav as key" format.

    The input file is assumed to contain lines of the following form:

        [[:space:]..]<key>[[:space:]..]=>[[:space:]..]<obj_str>[[:space:]..]

    or just (without keys):

        [[:space:]..]<obj_str>[[:space:]..]

    where <obj_str> is to be given as the only argument to the `constructor'
    when constructing the objects stored in the file.

    Arguments:
        fname -- path towards the file to read the objects from
        constructor -- function that will be called on each string stored in
            the file and whose result will become a value of the returned
            dictionary
        limit -- limit on the number of objects to read
        encoding -- the file encoding

    Returns a dictionary with objects constructed by `constructor' as values.

    """
    with codecs.open(fname, encoding=encoding) as infile:
        ret_dict = {}
        for line_idx, line in enumerate(islice(infile, 0, limit)):
            line = line.strip()
            if not line:
                continue

            parts = map(unicode.strip, line.split("=>", 1))

            # Distinguish the case with a key and without a key.
            if len(parts) == 2:
                key, utt_str = parts
            else:
                key = unicode(line_idx)
                utt_str = parts[0]

            try:
                ret_dict[key] = constructor(utt_str)
            except Exception:
                # TODO Probably should be logged.
                pass
    return ret_dict


def save_wavaskey(fname, in_dict, encoding='UTF-8', trans=lambda x: x):
    """
    Saves a dictionary of objects in the wave as key format into a file.

    :param file_name: name of the target file
    :param utt: a dictionary with the objects where the keys are the names of teh corresponding wave files
    :parma trans: a function which can transform a saved object
    :return: None
    """

    with codecs.open(fname, 'w', encoding=encoding) as outfile:
        for key in sorted(in_dict):
            outfile.write('{key} => {obj}\n'.format(key=key, obj=trans(in_dict[key])))
