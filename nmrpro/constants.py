#!/usr/bin/env python3


__all__ = [
    "BRUKER_FORMAT",
    "PIPE_FORMAT",
    "AUTODETECT_FORMAT",
    "SPARKY_FORMAT"
]


def _get_exclusive_constants(number):
    return range(1, 1+number)

def _get_inclusive_constants(number):
    return [ 1 << i for i in range(4) ]


(
    BRUKER_FORMAT,
    PIPE_FORMAT,
    AUTODETECT_FORMAT,
    SPARKY_FORMAT,
) = _get_exclusive_constants(4)


if __name__ == "__main__":
    assert (lambda x:x(10)[2]+x(10)[1] in x(10))(_get_exclusive_constants)
    assert (lambda x:x(10)[2]+x(10)[1] not in x(10))(_get_inclusive_constants)
