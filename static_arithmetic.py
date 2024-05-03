import collections
import functools
import math
import operator
from typing import Dict, Tuple, TypeVar, Union


T_SEGMENT = Tuple[int, int]


@functools.lru_cache()
def bin_power(n: int) -> int:
    return 2 ** n


T = TypeVar('T', bound=Union[str, int])


def longest_common_prefix(s1: T, s2: T) -> str:
    if isinstance(s1, int):
        s1 = bin_str(s1)
        s2 = bin_str(s2)

    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


@functools.lru_cache()
def bin_str(n: int) -> str:
    return bin(n)[2:].zfill(8)


def reverse_bit(bit: str) -> str:
    if bit == '1':
        return '0'
    if bit == '0':
        return '1'

    raise ValueError(bit)


def lshift(n: int, length: int, filler: int) -> int:
    bin_n = bin_str(n)
    return to_int(bin_n[length:] + str(filler) * length)


def to_int(s: str) -> int:
    return int(s, 2)


def extend_segment(segment: T_SEGMENT, window_size: int) -> T_SEGMENT:
    return 2 * segment[0] - bin_power(window_size - 1), 2 * segment[1] - bin_power(window_size - 1) + 1


def extend_count(segment: T_SEGMENT) -> int:
    l = bin_str(segment[0])
    h = bin_str(segment[1])

    if l[0] == h[0]:
        return 0

    ll = l[1:]
    hh = h[1:]

    extend_n = 0
    for i, l_symbol in enumerate(ll):
        h_symbol = hh[i]

        if l_symbol == '1' and h_symbol == '0':
            extend_n += 1
            continue

    return extend_n


def reverse_dict(d: dict) -> dict:
    return {value: key for key, value in d.items()}


def build_segments(text: str, *, window_size: int) -> Dict[str, T_SEGMENT]:
    N = bin_power(window_size)
    cnt = collections.Counter(text)

    segments = {}

    left = 0
    left_partial = 0
    for symbol, count in sorted(cnt.items(), key=operator.itemgetter(0)):
        left_partial += count
        right = math.ceil(left_partial * N / len(text)) - 1
        segments[symbol] = (left, right)
        left = right + 1

    return segments


def project_segment_on_segment(segment: T_SEGMENT, to: T_SEGMENT, *, window_size: int):
    ll = to[0] + math.ceil(segment[0] * (to[1] - to[0] + 1) / bin_power(window_size))
    hh = to[0] + math.ceil((segment[1] + 1) * (to[1] - to[0] + 1) / bin_power(window_size)) - 1

    return ll, hh


def encode_text(text: str, *, window_size: int) -> Tuple[str, Dict[str, T_SEGMENT]]:
    encoded_parts = []

    segments = build_segments(text, window_size=window_size)

    l = 0
    h = bin_power(window_size) - 1
    to_extend = 0   # bits

    lcp_not_changed = 0
    for symbol in text:
        segment = segments[symbol]
        ll, hh = project_segment_on_segment(segment, (l, h), window_size=window_size)

        lcp = longest_common_prefix(ll, hh)
        lcp_not_changed += 1
        if lcp:
            lcp_not_changed = 0
            out = lcp
            if to_extend:
                out = lcp[0] + reverse_bit(lcp[0]) * to_extend + lcp[1:]

            encoded_parts.append(out)

            l = lshift(ll, length=len(lcp), filler=0)
            h = lshift(hh, length=len(lcp), filler=1)

            to_extend = extend_count((l, h))
            for i in range(to_extend):
                l, h = extend_segment((l, h), window_size=window_size)

            continue

        l = ll
        h = hh

    return ''.join(encoded_parts) + '1' + lcp_not_changed * '0', segments


def find_symbol_in_segments(number: int, symbol_by_segment: Dict[T_SEGMENT, str]) -> Tuple[str, T_SEGMENT]:
    for segment, symbol in symbol_by_segment.items():
        if segment[0] <= number <= segment[1]:
            return symbol, segment

    raise ValueError(f"Can't find segment with number {number}")


def decode_text(encoded: str, *, window_size: int, segments: Dict[str, T_SEGMENT]) -> str:
    return 'NotImplemented'


if __name__ == '__main__':
    WINDOW_SIZE = 8
    TEXT = 'aaagggcacat'

    encoded, segments = encode_text(TEXT, window_size=WINDOW_SIZE)

    print(f'{encoded=}')

    decoded = decode_text(encoded, window_size=WINDOW_SIZE, segments=segments)
    print(f'{decoded=}')
