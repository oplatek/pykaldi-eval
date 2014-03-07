#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import codecs
import argparse
import sys


def findall(text, char, start=0, end=-1):
    idxs = list()
    if end == -1:
        end = len(text)
    nextidx = text.find(char, start, end)
    while nextidx != -1:
        idxs.append(nextidx)
        nextidx = text.find(char, nextidx + 1, end)
    return idxs


def split_by_comma(text):
    parentheses = 0
    splitList = []

    oldI = 0
    for i in xrange(len(text)):
        if text[i] == '(':
            parentheses += 1
        elif text[i] == ')':
            parentheses -= 1
            if parentheses < 0:
                raise ValueError("Missing a left parenthesis.")
        elif text[i] == ',':
            if parentheses == 0:
                if oldI == i:
                    raise ValueError(
                        "Split segment must not start with a comma.")
                else:
                    splitList.append(text[oldI:i].strip())
                    oldI = i + 1
    else:
        splitList.append(text[oldI:].strip())

    return splitList


def split_by(text, splitter,
             opening_parentheses='',
             closing_parentheses='',
             quotes="'\""):
    """
    Splits the input text at each occurrence of the splitter only if it is not
    enclosed in parentheses.

    text - the input text string
    splitter - multi-character string which is used to determine the position
               of splitting of the text
    opening_parentheses - an iterable of opening parentheses that has to be
                          respected when splitting, e.g. "{(" (default: '')
    closing_parentheses - an iterable of closing parentheses that has to be
                          respected when splitting, e.g. "})" (default: '')
    quotes - an iterable of quotes that have to come in pairs, e.g. '"'

    """
    split_list = []

    # Interpret the arguments.
    parentheses_counter = dict((char, 0)
                               for char in opening_parentheses + quotes)
    map_closing_to_opening = dict(zip(closing_parentheses,
                                      opening_parentheses))

    segment_start = 0
    segment_end = 0
    while segment_end < len(text):
        cur_char = text[segment_end]
        if cur_char in opening_parentheses:
            parentheses_counter[cur_char] += 1
        elif cur_char in closing_parentheses:
            parentheses_counter[map_closing_to_opening[cur_char]] -= 1

            if parentheses_counter[map_closing_to_opening[cur_char]] < 0:
                raise ValueError(("Missing an opening parenthesis for: {par} "
                                  "in the text: {text}").format(par=cur_char,
                                                                text=text))
        elif cur_char in quotes:
            parentheses_counter[cur_char] = (
                parentheses_counter[cur_char] + 1) % 2
        elif text[segment_end:].startswith(splitter):
            # Test that all parentheses are closed.
            if not any(parentheses_counter.values()):
                split_list.append(text[segment_start:segment_end].strip())
                segment_end += len(splitter)
                segment_start = segment_end

        segment_end += 1
    else:
        split_list.append(text[segment_start:segment_end].strip())

    return split_list


def parse_command(command):
    """Parse the command name(var1="val1",...) into a dictionary structure:

      E.g. call(destination="1245",opt="X") will be parsed into:

        { "__name__":    "call",
          "destination": "1245",
          "opt":         "X"}

      Return the parsed command in a dictionary.
    """

    try:
        i = command.index('(')
    except ValueError:
        raise Exception(
            "Parsing error in: %s. Missing opening parenthesis." % command)

    name = command[:i]
    d = {"__name__": name}

    # remove the parentheses
    command_svs = command[i + 1:len(command) - 1]

    if not command_svs:
        # there are no parameters
        return d

    command_svs = split_by(command_svs, ',', '', '', '"')

    for command_sv in command_svs:
        i = split_by(command_sv, '=', '', '', '"')
        if len(i) == 1:
            raise Exception(("Parsing error in: {cmd}: {slot}. There is only "
                             "variable name")
                            .format(cmd=command, slot=unicode(i)))
        elif len(i) == 2:
            # There is a slot name and a value.
            d[i[0]] = i[1][1:-1]
        else:
            raise Exception("Parsing error in: %s: %s" % (command, str(i)))

    return d


def min_edit_dist(target, source):
    ''' Computes the min edit distance from target to source. '''

    n = len(target)
    m = len(source)

    distance = [[0.0 for i in range(m)] for j in range(n)]

    for i in range(1, n):
        distance[i][0] = distance[i - 1][0] + 1

    for j in range(1, m):
        distance[0][j] = distance[0][j - 1] + 1

    for i in range(1, n):
        for j in range(1, m):
            distance[i][j] = min(distance[i - 1][j] + 1,
                                 distance[i][j - 1] + 1,
                                 distance[i - 1][j - 1] + (0 if target[i] == source[j] else 2))
    return distance[n - 1][m - 1]


def min_edit_ops(target, source, cost=lambda insertions, deletions, substitutions: insertions + deletions + 2.0 * substitutions):
    """ Computes the min edit operations from target to source.

    :param target: a target sequence
    :param source: a source sequence
    :param cost: an expression for computing cost of the edit operations
    :return: a tuple of (insertions, deletions, substitutions)

    """
    n = len(target)
    m = len(source)
    ops = [[(0, 0, 0) for i in range(m + 1)] for j in range(n + 1)]
    for i in range(1, n + 1):
        ops[i][0] = (ops[i - 1][0][0] + 1, ops[i - 1][0][1], ops[i - 1][0][2])
    for j in range(1, m + 1):
        ops[0][j] = (ops[0][j - 1][0], ops[0][j - 1][1] + 1, ops[0][j - 1][2])
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            insertion = cost(ops[i - 1][j][0] + 1,
                             ops[i - 1][j][1], ops[i - 1][j][2])
            deletion = cost(ops[i][j - 1][0], ops[i][j - 1]
                            [1] + 1, ops[i][j - 1][2])
            if source[j - 1] != target[i - 1]:
                substitution = cost(ops[i - 1][j - 1][0], ops[i - 1]
                                    [j - 1][1], ops[i - 1][j - 1][2] + 1)
            else:
                substitution = cost(ops[i - 1][j - 1][0], ops[i - 1]
                                    [j - 1][1], ops[i - 1][j - 1][2])

            if substitution <= insertion and substitution <= deletion:
                if source[j - 1] != target[i - 1]:
                    ops[i][j] = (ops[i - 1][j - 1][0], ops[i - 1]
                                 [j - 1][1], ops[i - 1][j - 1][2] + 1)
                else:
                    ops[i][j] = (ops[i - 1][j - 1][0], ops[i - 1]
                                 [j - 1][1], ops[i - 1][j - 1][2])
            elif insertion <= deletion and insertion <= deletion:
                ops[i][j] = (ops[i - 1][j][0] + 1, ops[i - 1]
                             [j][1], ops[i - 1][j][2])
            elif deletion <= insertion and deletion <= substitution:
                ops[i][j] = (ops[i][j - 1][0], ops[i][j - 1]
                             [1] + 1, ops[i][j - 1][2])
            else:
                raise Exception("min_edit_ops unexpected state")
    return ops[n][m]


class Escaper(object):

    """
    Creates a customised escaper for strings.  The characters that need
    escaping, as well as the one used for escaping can be specified.

    """
    # TODO Write tests.

    # Constants for types of characters in a text that has been escaped.
    ESCAPER = 0
    ESCAPED = 1
    NORMAL = 2

    def __init__(self, chars="'\"", escaper='\\', re_flags=0):
        """Constructs an escaper for escaping the specified characters.

        Arguments:
            chars -- a collection of characters to escape (default: "'\"")
            escaper -- the character used as the escaper (default: '\\')
            re_flags -- any regex flags (as defined in the built-in `re'
                module) to use when building the escaping regexp (default: 0)

        """
        self.rx = re.compile(Escaper.re_literal_list(chars + escaper),
                             re_flags)
        escaper_lit = Escaper.re_literal(escaper)
        self.sub = escaper_lit + '\\g<0>'
        self.unrx = re.compile(escaper_lit + '(.)')
        self.unsub = '\\1'

    _re_br_spec_chars_rx = re.compile('[]\\\\^-]')

    @staticmethod
    def re_literal_list(chars):
        """
        Builds a [] group for a regular expression that matches exactly the
        characters specified.

        """
        return '[{esced}]'.format(
            esced=Escaper._re_br_spec_chars_rx.sub('\\\\\\g<0>', chars))

    _re_combining_chars = '1234567890AbBdDsSwWZafnrtvx'

    @staticmethod
    def re_literal(char):
        """
        Escapes the character so that when it is used in a regexp, it matches
        itself.
        """
        return char if (char in Escaper._re_combining_chars) else ('\\' + char)

    def escape(self, text):
        """Escapes the text using the parameters defined in the constructor."""
        return self.rx.sub(self.sub, text)

    def unescape(self, text):
        """
        Unescapes the text using the parameters defined in the constructor."""
        # TODO Test whether this picks disjunct matches (yes, it should).
        return self.unrx.sub(self.unsub, text)

    def annotate(self, esced):
        """
        Annotates each character of a text that has been escaped whether:

            Escaper.ESCAPER - it is the escape character
            Escaper.ESCAPED - it is a character that was escaped
            Escaper.NORMAL  - otherwise.

        It is expected that only parts of the text may have actually been
        escaped.

        Returns a list with the annotation values, co-indexed with characters
        of the input text.

        """
        annion = [Escaper.NORMAL] * len(esced)
        for match in self.unrx.finditer(esced):
            first = match.start()
            annion[first] = Escaper.ESCAPER
            annion[first + 1] = Escaper.ESCAPED
        return annion


def escape_special_characters_shell(text, characters="'\""):
    """
    Simple function that tries to escape quotes.  Not guaranteed to produce
    the correct result!!  If that is needed, use the new `Escaper' class.

    """
    for character in characters:
        text = text.replace(character, '\\' + character)
    return text


def score_file(reftext, testtext):
    """
    Computes ASR scores between reference and test word strings.

    :param reftext:
    :param testtext:
    :return: a tuple with percentages of correct, substitutions, deletions, insertions, error rate, and a number of reference words.
    """
    ii, dd, ss, nn = 0.0, 0.0, 0.0, 0.0

    for utt_idx in sorted(reftext):
        r = re.sub(ur"\b_\w+_\b", r"",
                   unicode(reftext[utt_idx]).lower(), flags=re.UNICODE).split()
        t = re.sub(ur"\b_\w+_\b", r"",
                   unicode(testtext[utt_idx]).lower(), flags=re.UNICODE).split()
#        r = unicode(reftext[utt_idx]).lower().split()
#        t = unicode(testtext[utt_idx]).lower().split()
        i, d, s = min_edit_ops(t, r)

        ii += i
        dd += d
        ss += s

        nn += len(r)

#        print "Ref:", unicode(r)
#        print "Tst:", unicode(t)
#        print i, d, s, len(r)
#        print ii, dd, ss, nn
#        print

    return (nn - ss - dd) / nn * 100, ss / nn * 100, dd / nn * 100, ii / nn * 100, (ss + dd + ii) / nn * 100, nn


def score(fn_reftext, fn_testtext, outfile=sys.stdout, encoding='UTF-8'):
    with codecs.open(fn_reftext, encoding=encoding) as rr:
        with codecs.open(fn_testtext, encoding=encoding) as rt:
            reftext = dict([line.split(' ', 1) for line in rr.readlines()])
            testtext = dict([line.split(' ', 1) for line in rt.readlines()])

            corr, sub, dels, ins, wer, nwords = score_file(reftext, testtext)

            m = """
            Please note that the scoring is implicitly ignoring all non-speech events.

            Ref: {r}
            Tst: {t}
            |==============================================================================================|
            |            | # Sentences  |  # Words  |   Corr   |   Sub    |   Del    |   Ins    |   Err    |
            |----------------------------------------------------------------------------------------------|
            | Sum/Avg    |{num_sents:^14}|{num_words:^11.0f}|{corr:^10.2f}|{sub:^10.2f}|{dels:^10.2f}|{ins:^10.2f}|{wer:^10.2f}|
            |==============================================================================================|
            """.format(r=fn_reftext, t=fn_testtext, num_sents=len(reftext), num_words=nwords, corr=corr, sub=sub, dels=dels, ins=ins, wer=wer)

            outfile.write(m)
            outfile.write("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
    Compute ASR scores for ASR output against reference text.
    The scoring implicitly ignores non-speech events in comparison.

    The files structures must be as follows:
      text_name    => text_content
      ----------------------------------------
      0000001.wav => I want Chinese food
      0000002.wav => Give me the phone number

    The text from the test file and the reference file is matched based on the text_name.
    """)

    parser.add_argument('refsem', action="store",
                        help='a file with reference semantics')
    parser.add_argument('testsem', action="store",
                        help='a file with tested semantics')

    args = parser.parse_args()

    score(args.refsem, args.testsem)
