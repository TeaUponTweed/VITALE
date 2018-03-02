import pandas as pd
import numpy as np
from searchAlgorithms import evolutionary_search


def Pr_elo(elo_diff, div=400):
    """ Return the probability of a win given elo difference
    """
    return 1 / (10**( -1.*(elo_diff)/div ) + 1)


def rating_adjuster(Ri, params, elo_diff, MoV):
    """
    Adjust a team's Elo rating based on the outcome of the game
    A, B, K: Parameters
    Ri:         Initial elo rating
    MoV:        Margin of victory (this_score - other_score)
    elo_diff:   Elo delta (elo_winner - elo_loser)
    """
    MoV_mult = 1. / (params[0] + params[1]*elo_diff)
    MoV_adj = np.sign(MoV) * np.log(np.abs(MoV) + 1)
    new_Ri = Ri + params[2] * MoV_adj * MoV_mult
    return new_Ri


def log_loss(prob):
    return -np.mean(np.log(prob))


def obj_fun(elo_params, init_elo, data, teams):
    team_elos = {ID: init_elo for ID in teams['TeamID']}
    N = data.shape[0]
    win_prob = np.zeros(N)
    seasons = np.array(data['Season'])
    w_ID = np.array(data['WTeamID'])
    l_ID = np.array(data['LTeamID'])
    w_score = np.array(data['WScore'])
    l_score = np.array(data['LScore'])
    current_season = seasons[0]
    for ix in range(N):
        if seasons[ix] > current_season:
            current_season = seasons[ix]
            team_elos = {ID: init_elo for ID in teams['TeamID']}
            print("Season:", current_season)
        elo_w = team_elos[w_ID[ix]]
        elo_l = team_elos[l_ID[ix]]
        elo_diff = elo_w - elo_l
        MoV = w_score[ix] - l_score[ix]
        win_prob[ix] = Pr_elo(elo_diff)
        team_elos[w_ID[ix]] = rating_adjuster(elo_w, elo_params, elo_diff, MoV)
        team_elos[l_ID[ix]] -= team_elos[w_ID[ix]] - elo_w
    return log_loss(win_prob)



if __name__=="__main__":

    init_elo = 1500.
    elo_params = [1., 1e-4, 10.]
    data = pd.read_csv('data/DataFiles/RegularSeasonCompactResults.csv')
    teams = pd.read_csv('data/DataFiles/Teams.csv')

    data = data.loc[np.logical_and(data['Season']>=2003, data['Season']<2014)]
    data = data.reset_index(drop=True)

    pop, bf = evolutionary_search(10, 10, 0.5, 0.5, obj_fun, elo_params, init_elo, data, teams)