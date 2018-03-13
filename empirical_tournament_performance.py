import sys, itertools

import matplotlib.pyplot as plt
import pandas as pd


def groupby(itr, key):
    data = sorted(itr, key=key)
    yield from itertools.groupby(data, key)


def main():
    seed_file = sys.argv[1]
    tourny_file = sys.argv[2]
    seed_df = pd.read_csv(seed_file)
    tourny_df = pd.read_csv(tourny_file)
    # get seeds
    seeds = {}
    for season, seed, team_id in seed_df.values:
        seed = int(seed[1:3])
        print(seed)
        # if '16' in seed:
        #     seed = 16
        # else:
        #     seed = int(seed)
        seeds[season, team_id] = seed

    # add seed to tourny df
    wseeds = [seeds[season, wteam_id] for season, wteam_id in zip(tourny_df['Season'], tourny_df['WTeamID'])]
    lseeds = [seeds[season, lteam_id] for season, lteam_id in zip(tourny_df['Season'], tourny_df['LTeamID'])]
    point_diffs = [wscore - lscore for wscore, lscore in zip(tourny_df['WScore'], tourny_df['LScore'])]
    def gen():
        for wseed, lseed, diff in zip(wseeds, lseeds, point_diffs):
            if lseed > wseed:
                diff = - diff
                wseed, lseed = lseed, wseed
            yield wseed, lseed, diff

    for (wseed, lseed), data in groupby(gen(), lambda x: x[:2]):
        _, _, diffs = zip(*data)
        plt.hist(diffs)
        plt.title('{} {}'.format(wseed, lseed))
        plt.show()
 

if __name__ == '__main__':
    main()
