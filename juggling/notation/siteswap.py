import re

from .base import JugglingNotation
from ..pattern import Pattern


__all__ = ['Siteswap', 'siteswap_char_to_int', 'siteswap_int_to_char', 'is_valid_siteswap_syntax',
           'convert_str_to_beat_list', 'convert_char_to_beat']


def siteswap_char_to_int(char):
    # type: str -> int
    """ Converts a siteswap character to a digit """
    if not isinstance(char, str):
        raise ValueError("Invalid SiteSwap character: '{}'".format(char))
    if len(char) != 1:
        raise ValueError('Invalid SiteSwap character, too many characters')
    try:
        return int(char.lower(), 36)
    except ValueError:
        raise ValueError("Invalid SiteSwap character: '{}'".format(char))


def siteswap_int_to_char(digit):
    if not isinstance(digit, int):
        raise ValueError("Digit must be between an integer 0 and 36 [0:Z]")
    if digit < 0 or digit > 35:
        raise ValueError("Digit must be between an integer 0 and 36 [0:Z]")
    if digit < 10:
        return str(digit)
    return chr(ord("a") + (digit-10))


TOSS_RE = r'([0-9a-z]x?)'
PASS_TOSS_RE = r'([0-9a-z]x?(p{num_jugglers})?)'
MULTIPLEX_RE = r'\[{}+\]'.format(TOSS_RE)
PASS_MULTIPLEX_RE = r'\[{}+\]'.format(PASS_TOSS_RE)
SYNC_BASE_RE = r'(\(({toss}|{multi}),({toss}|{multi})\))\*?'
SYNC_RE = SYNC_BASE_RE.format(toss=TOSS_RE, multi=MULTIPLEX_RE)
PASS_SYNC_RE = SYNC_BASE_RE.format(toss=PASS_TOSS_RE, multi=MULTIPLEX_RE)
BEAT_RE = r'({}|{}|{})'.format(TOSS_RE, MULTIPLEX_RE, SYNC_RE)
PASS_BEAT_RE = r'({}|{}|{})'.format(PASS_TOSS_RE, PASS_MULTIPLEX_RE, PASS_SYNC_RE)
SOLO_SITESWAP_RE = re.compile(r'^{}+$'.format(BEAT_RE), re.IGNORECASE | re.VERBOSE)
PASS_RE = r'<({beat})(\|{beat})+>'.format(beat=PASS_BEAT_RE)


def is_valid_siteswap_syntax(pattern, num_jugglers=1, return_match=False):
    # type: (str, int) -> bool or (bool, match)
    """
    Checks whether the given pattern is in valid siteswap syntax.

    >>> is_valid_siteswap_syntax('441') == True
    >>> is_valid_siteswap_syntax('$$92') == False
    >>> matched, match_object = is_valid_siteswap_syntax('(6x,4)*', return_match=True)

    :param pattern: A string of the siteswap to check
    :param num_jugglers:  Number of jugglers involved in the siteswap. This determines whether
        to allow passing notation and also whether the passing notation needs to include the
        juggler being passed to.
    :param return_match: Affects whether or not the match object is returned as well. If True,
        this function will return a tuple, (bool, match). The bool is whether or not the syntax is valid. If
        the syntax is valid, a regex match object is returned. Otherwise None is returned
    :return: A bool whether or not the syntax is valid.
    """
    pattern = str(pattern)

    if num_jugglers < 1:
        raise ValueError("Invalid number of jugglers: {}".format(num_jugglers))
    elif num_jugglers > 1:
        if num_jugglers > 2:
            pass_re = "^({})+$".format(PASS_RE.format(
                num_jugglers="[1-{}]".format(num_jugglers)))
        else:
            pass_re = "^({})+$".format(PASS_RE.format(num_jugglers=""))
        m = re.match(pass_re, pattern, re.IGNORECASE | re.VERBOSE)
    else:
        m = SOLO_SITESWAP_RE.match(pattern)

    if return_match:
        return m is not None, m
    else:
        return m is not None


def convert_char_to_beat(beat_str):
    # type: (str) -> (int or list)
    """ Converts a single siteswap beat into a :class:`Pattern` beat """
    print("converting: {}".format(beat_str))
    if beat_str.startswith('['):
        return [siteswap_char_to_int(_) for _ in beat_str[1:-1]]
    elif beat_str.startswith('('):
        # TODO: This is wrong, just put it in here for the time being because its almost right
        return [_ for _ in convert_str_to_beat_list(beat_str[1:-1].split(','))]
    else:
        return siteswap_char_to_int(beat_str)


def convert_str_to_beat_list(siteswap):
    # type: (str) -> list
    """ Converts a siteswap string to a :class:`Pattern` beat list """
    return [convert_char_to_beat(_.group()) for _ in re.finditer(BEAT_RE, siteswap, re.IGNORECASE)]


class Siteswap(JugglingNotation):
    """ Siteswap notation """
    def __init__(self, notation_pattern, raise_invalid=False):
        notation_pattern = ''.join(str(notation_pattern))  # removes all whitespace characters
        super(Siteswap, self).__init__(notation_pattern=notation_pattern, raise_invalid=raise_invalid)

        if self.is_valid_syntax:
            self.pattern = Pattern(convert_str_to_beat_list(self.notation_pattern))

    @property
    def is_valid(self):
        # TODO: implement site swap validation
        return True

    @property
    def is_valid_syntax(self):
        # return cached value if we have it
        return is_valid_siteswap_syntax(self.notation_pattern)
