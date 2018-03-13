import itertools as it
from math import log

import matplotlib.pyplot as plt

from bracket import gen_windows, gen_tiers, setup_bracket, probability_a_beats_b


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)


def get_probabilities(teams, dumb=False):
    P = {}
    for t1 in teams:
        for t2 in teams:
            if t1.rank == t2.rank:
                continue
            p = probability_a_beats_b(t1, t2)
            if dumb:
                if p > 0.5:
                    p = 0.80
                else:
                    p = 0.20
            P[t1.rank, t2.rank] = p
            P[t2.rank, t1.rank] = 1 - p

    return P


def score_playout(playout):
    P = get_probabilities(playout[0])
    Pdumb = get_probabilities(playout[0], dumb=True)
    logloss = 0
    dumb_logloss = 0
    n = 0
    for tier1, tier2 in pairwise(playout):
        next_ranks = set(team.rank for team in tier2)
        for team1, team2 in gen_windows(tier1, 2):
            team1wins = int(team1.rank in next_ranks)
            n += 1
            p = P[team1.rank, team2.rank]
            pdumb = Pdumb[team1.rank, team2.rank]
            logloss += team1wins * log(p) + (1  - team1wins) * log(1-p)
            dumb_logloss += team1wins * log(pdumb) + (1  - team1wins) * log(1-pdumb)
    return -logloss/n, -dumb_logloss/n




def get_cdf_xy(data):
    x = sorted(data)
    N = len(x)
    y = [i/N for i in range(1, N+1)]
    return x, y

def main():
    scores, dumb_scores = [], []
    for _ in range(50):
        starting_bracket = setup_bracket()
        playout = list(gen_tiers(starting_bracket))
        # for _ in playout:
        #     print(_)
        logloss, dumb_logloss = score_playout(playout)
        scores.append(logloss)
        dumb_scores.append(dumb_logloss)
    plt.plot(*get_cdf_xy(scores), label='not dumb')
    plt.plot(*get_cdf_xy(dumb_scores), label='dumb')
    # plt.axvline(.481309, label='best achieved score 2016')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
