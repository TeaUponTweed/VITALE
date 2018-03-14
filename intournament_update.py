import sys, itertools, os
from pprint import pprint

import matplotlib.pyplot as plt
import pandas as pd

from expected_log_loss import pairwise, score_playout
from bracket import gen_windows
from logistic_regression import get_year_t1_t2

class Team:
    def __init__(self, team_id, p_weights=None):
        self.team_id = team_id
        self.p_weights = p_weights or {team_id: 1}

    def win(self, other_team_id, win_weight):
        assert other_team_id not in self.p_weights, other_team_id
        assert 0 < win_weight < 1, win_weight
        self.p_weights[other_team_id] = win_weight # 1 - prob_win?

    def probability_of_beating(self, other_team, prob_func):
        prob = 0
        total_weight = 0
        for tid1, w1 in self.p_weights.items():
            for tid2, w2 in other_team.p_weights.items():
                assert tid1 != tid2
                prob += prob_func(tid1, tid2) * w1 * w2
                total_weight += w1 * w2
        # normalize
        prob = prob/total_weight
        assert 0 < prob < 1
        return prob

    def __repr__(self):
        return 'T({})'.format(self.team_id)

def main():
    submission_file = os.path.join('output', 'logreg_seed_starter.csv')
    tournament_file = os.path.join('WData', 'WNCAATourneyCompactResults.csv ')
    probabilities = load_probabilities(submission_file)
    for season, playout in gen_playouts(tournament_file):
        if season not in probabilities:
            continue
        P = probabilities[season]
        def probability_a_beats_b(a, b):
            return P[a.team_id, b.team_id]

        updated_playout = [[Team(t.team_id) for t in playout[0]]]
        for competitors, winners in pairwise(playout):
            winner_ids = set(winner.team_id for winner in winners)
            updated_winners = []
            for team1, team2 in gen_windows(competitors, 2):
                winner = team1 if team1.team_id in winner_ids else team2
                loser = team2 if team1.team_id in winner_ids else team1
                updated_winner = Team(winner.team_id, winner.p_weights.copy())
                # TODO learn suprise
                suprise = probability_a_beats_b(loser, winner)
                updated_winner.win(loser.team_id, suprise)
                updated_winners.append(winner)
            updated_playout.append(updated_winners)
        # score original playout
        print(season, 'original', score_playout(playout, probability_a_beats_b))
        # score updated playout
        def get_prob_from_team_ids(tid1, tid2):
            return P[tid1, tid2]
        def updated_probability_a_beats_b(t1, t2):
            return t1.probability_of_beating(t2, get_prob_from_team_ids)
        print(season, 'updated', score_playout(updated_playout, updated_probability_a_beats_b))


def load_probabilities(submission_file):
    out = {}
    submission_df = pd.read_csv(submission_file)
    for _, row in submission_df.iterrows():
        year, t1, t2 = get_year_t1_t2(row.ID)
        if year not in out:
            out[year] = {}
        p = row.Pred
        out[year][t1, t2] = p
        out[year][t2, t1] = 1 - p
    return out


def gen_playouts(csv):
    full_df = pd.read_csv(csv)
    for season, season_df in full_df.groupby('Season', as_index=False):
        if season_df.shape[0] > 63:
            ndrop = season_df.shape[0] - 63
            season_df = season_df.iloc[ndrop:]
        assert season_df.shape[0] == 63
        start_ix = 0
        playout = []
        season_df = season_df.reset_index()
        for ngames in (32, 16, 8, 4, 2, 1):
            winners = season_df.loc[start_ix:start_ix+ngames-1,'WTeamID'].values
            losers = season_df.loc[start_ix:start_ix+ngames-1,'LTeamID'].values
            assert len(winners) == len(losers) == ngames
            contenders = [Team(int(team_id)) for team_id in itertools.chain(*zip(winners, losers))]
            playout.append(contenders)
            start_ix += ngames

        playout.append([Team(int(season_df.iloc[-1]['WTeamID']))])
        yield int(season), playout
 

if __name__ == '__main__':
    main()