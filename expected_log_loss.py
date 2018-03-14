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

            P[t1.rank, t2.rank] = p
            P[t2.rank, t1.rank] = 1 - p

    return P


def score_playout(playout, probfunc):
    logloss = 0
    n = 0
    for competitors, winners in pairwise(playout):
        winner_ids = set(team.team_id for team in winners)
        for team1, team2 in gen_windows(competitors, 2):
            team1wins = int(team1.team_id in winner_ids)
            n += 1
            p = probfunc(team1, team2)
            logloss += team1wins * log(p) + (1  - team1wins) * log(1-p)

    return -logloss/n


def get_cdf_xy(data):
    x = sorted(data)
    N = len(x)
    y = [i/N for i in range(1, N+1)]
    return x, y

def main():
    scores, dumb_scores = [], []
    for _ in range(50):
        starting_bracket = setup_bracket()
        P = get_probabilities(starting_bracket)
        def get_prob(t1, t2):
            return P[t1.rank, t2.rank]

        def get_dumb_prob(t1, t2):
            p = get_prob(t1, t2)
            return 0.8 if p > 0.5 else 0.2

        playout = list(gen_tiers(starting_bracket))

        logloss = score_playout(playout, get_prob)
        dumb_logloss = score_playout(playout, get_dumb_prob)
        scores.append(logloss)
        dumb_scores.append(dumb_logloss)
    plt.plot(*get_cdf_xy(scores), label='not dumb')
    plt.plot(*get_cdf_xy(dumb_scores), label='dumb')
    # plt.axvline(.481309, label='best achieved score 2016')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()
