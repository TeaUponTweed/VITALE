import pandas as pd
import bisect

def compile_data_with_rankings(dir_prefix='mens_'):
    # Load data
    massey_data = pd.read_csv(dir_prefix+'data/MasseyOrdinals/MasseyOrdinals.csv')
    reg_season_data = pd.read_csv(dir_prefix+'data/DataFiles/RegularSeasonCompactResults.csv')
    alt_tourney_data = pd.read_csv(dir_prefix+'data/DataFiles/SecondaryTourneyCompactResults.csv')
    ncaa_tourney_data = pd.read_csv(dir_prefix+'data/DataFiles/NCAATourneyCompactResults.csv')

    reg_season_data['GameType'] = 'REG'
    alt_tourney_data['GameType'] = 'ALT_TOURN'
    ncaa_tourney_data['GameType'] = 'NCAA_TOURN'

    # Compile data into one array
    all_frames = [reg_season_data, alt_tourney_data.drop('SecondaryTourney', axis=1), ncaa_tourney_data]
    all_data = pd.concat(all_frames).reset_index(drop=True)

    # Restrict data to seasons with rankings
    ix_rm = all_data.index[all_data['Season'] < min(massey_data['Season'])]
    all_data = all_data.drop(ix_rm)
    all_data = all_data.sort_values(['Season', 'DayNum']).reset_index(drop=True)
    massey_data = massey_data.sort_values(['Season', 'RankingDayNum', 'SystemName']).reset_index(drop=True)
    rankers = pd.unique(massey_data['SystemName'])

    # Get massey dict
    massey_dict = {}
    for key, block in massey_data.groupby(['Season', 'SystemName', 'TeamID']):
        massey_dict[key] = block

    def gen_rows():
        current_season = 0
        cols = all_data.columns
        for row in all_data.values:
            row = dict(zip(cols, row))
            if row['Season'] > current_season:
                print(row['Season'])
                current_season = row['Season']
            for prefix in 'WL':
                for ranker in rankers:
                    key = (row['Season'], ranker, row[prefix+'TeamID'])
                    try:
                        rel_data = massey_dict[key]
                        ix = bisect.bisect_left(rel_data['RankingDayNum'].values, row['DayNum'])
                        rank = rel_data['OrdinalRank'].values[ix-1] if ix > 0 else -1
                    except KeyError:
                        rank = -1
                    row[prefix+'_'+ranker] = rank
            yield row

    all_data_new = pd.DataFrame(gen_rows())
    all_data_new.to_csv(dir_prefix+'data/DataFiles/CompliledRankingData.csv')