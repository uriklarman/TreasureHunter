from math import pow
import itertools
from random import Random

__author__ = 'uriklarman'

SEED = 1609


def random_product(*args, **kwds):
    pools = map(tuple, args) * kwds.get('repeat', 1)
    rand = kwds.get('rand')
    return tuple(rand.choice(pool) for pool in pools)


def pseudo_random_combinations(values, tuple_size, result_limit=False, avoid_all_combinations=False):
    rand = Random()
    rand.seed(SEED)

    if not result_limit:
        result_limit = int(pow(len(values),tuple_size))
    else:
        result_limit = int(min(int(pow(len(values),tuple_size)), result_limit))

    if avoid_all_combinations:
        combinations = []
        combinations_set = set()
        while len(combinations_set) < result_limit:
            if len(combinations_set) %10000 == 0:
                print 'len(combinations_set): ', len(combinations_set)
            combo = random_product(values, rand=rand, repeat=tuple_size)
            if combo not in combinations_set:
                combinations.append(combo)
                combinations_set.add(combo)
        return combinations

    else:
        combinations = [x for x in itertools.product(values, repeat=tuple_size)]
        rand.shuffle(combinations)
        return combinations[:result_limit]


# returns an iterable, which only allocate values when they are needed
def create_ordered_combinations(values, tuple_size):
    return itertools.product(values, repeat=tuple_size)

def gen_subsets_special(full_set, M):
    # generate randomish M-subsets of full_set, "far apart".
    import random
    from random import sample
    # random.seed(SEED)
    elements = list(full_set)
    allix = set(range(len(elements)))
    takefrom = allix.copy()

    def destructive_sample(n):
        # Remove a random n-subset from takefrom, & return it.
        s = set(sample(takefrom, n))
        takefrom.difference_update(s)
        return s

    while True:
        if len(takefrom) >= M:
            # Get everything from takefrom.
            ix = destructive_sample(M)
        else:
            # We need to take all of takefrom, and more.
            ix = takefrom
            takefrom = allix - ix
            ix |= destructive_sample(M - len(ix))
        assert len(ix) == M
        yield frozenset(elements[i] for i in ix)

if __name__ == '__main__':
    a = pseudo_random_combinations(range(100),3,result_limit=100000,avoid_all_combinations=True)
    b = pseudo_random_combinations(range(100),3,result_limit=100000,avoid_all_combinations=True)
    print 'done!: ', len(a), a[:5]
    print 'done!: ', len(b), b[:5]
