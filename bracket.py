#!/usr/bin/env python3
import math, random
from typing import List, Iterable, Generic, TypeVar, Tuple
T = TypeVar('T')


class Team(object):
    def __init__(self, elo: int):
        self.elo = elo
        self.rank = None

    def __repr__(self):
        return str(self.rank)

def Pr_elo(elo_diff: int, div: int=400) -> float:
    '''
    Probability a team wins
    '''
    return 1 / (10**(-1*(elo_diff)/div) + 1)

def probability_a_beats_b(a: Team, b: Team) -> float:
    return Pr_elo(a.elo - b.elo)

def split(itr: Iterable[T], n: int) -> List[List[T]]:
    '''
    splits itr into n different sublists
    '''
    out = [[] for _ in range(n)]
    ix = 0
    for item in itr:
        out[ix].append(item)
        ix += 1
        ix = ix % n
    return out

def gen_windows(itr, n):
    itr = iter(itr)
    while True:
        win = []
        for _ in range(n):
            win.append(next(itr))
        yield win


def gen_tiers(bracket: List[Team], verbose: bool = False):
    yield bracket
    while len(bracket) > 1:
        def gen_winners(bracket):
            for t1, t2 in gen_windows(bracket, 2):
                p = probability_a_beats_b(t1, t2)
                t1wins = random.random() < p
                if t1wins != (t1.rank < t2.rank):
                    if verbose:
                        print(t1, t2, p)                
                        if t2.rank > t1.rank:
                            print('wow {} beat {}'.format(t2, t1))
                        else:
                            print('wow {} beat {}'.format(t1, t2))
                if t1wins:
                    yield t1
                else:
                    yield t2

        bracket = list(gen_winners(bracket))
        yield bracket

    yield bracket


def simulate_play(bracket):
    for _ in gen_tiers(bracket, True):
        pass

def _next_layer(pls):
    out=[]
    length = len(pls)*2+1
    for d in pls:
        out.append(d)
        out.append(length-d)
    return out

def seeding(nplayers):
    rounds = math.log(nplayers)/math.log(2)-1
    seed = [1,2]
    for _ in range(int(rounds)):
        seed = _next_layer(seed)
    return [s - 1 for s in seed]


def main():
    teams = setup_bracket()
    simulate_play(teams)


def setup_bracket() -> List[Team]:
    teams = [Team(random.randint(1250, 1750)) for _ in range(32)]
    seeding_ixs = seeding(len(teams))
    teams = sorted(teams, key=lambda  x: x.elo, reverse=True)
    for i, team in enumerate(teams):
        team.rank = i + 1
    teams = [teams[ix] for ix in seeding_ixs]
    return teams


if __name__ == '__main__':
    main()
