import argparse
import itertools


def str2bool(v):
    """Nice function to convert cmd-line args to bool.

    """

    if v.lower() in ('yes', 'true', 't', 'y', '1'):

        return True

    elif v.lower() in ('no', 'false', 'f', 'n', '0'):

        return False

    else:

        raise argparse.ArgumentTypeError('Boolean value expected.')


def flatten(listoflists):
    """Flatten one level of nesting.

    """
    return itertools.chain.from_iterable(listoflists)


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    num_active = len(iterables)
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)

    while num_active:

        try:

            for next in nexts:

                yield next()

        except StopIteration:

            # Remove the iterator we just exhausted from the cycle.
            num_active -= 1
            nexts = itertools.cycle(itertools.islice(nexts, num_active))


if __name__ == '__main__':

    # from charlie2.tests.trails import phases, phase_type, blaze_positions
    # it = itertools.zip_longest(phases, phase_type, blaze_positions)
    # a = it.__next__()
    # print(a)
    letters = 'abcdefghijklmnopqrstuvwxy'
    print(len(letters))
