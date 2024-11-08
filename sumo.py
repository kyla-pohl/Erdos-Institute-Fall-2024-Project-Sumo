import re

def get_ordinal_rank(df):
    """
    Takes a dataframe and finds the 'unique' ranks and generates a numberic rank that can be sorted, returns a dictionary that
    matches the rikishi1 rank with the sortable numeric rank
    """
    #Yokozuna (Y) > Ozeki (O) > Sekiwake (S) > Komusubi (K) > Maegashira (M) > Juryo (J) > Makushita (Ms)
    #Y > O > S > K > M > J > Ms
    #Turning the rankings into unique(?) numbers
    #Assigning value 1-7 for the division
    #Padding the single digit ranks with zeros so it sorts correctly : 1->01
    #Assigning values for ('w','e','(e/w)HD') made e=eHD, and w=WHD for now
    
    unique_ranks = df['rikishi1_rank'].unique()
    rank_dict = {}
    div = {'Y':'1', 'O':'2', 'S':'3', 'K':'4', 'M':'5', 'J':'6', 'Ms':'7'}
    car = {'e':'1', 'w':'2', 'eHD':'1', 'wHD':'2'}
    for key in unique_ranks:
        value = re.split(r'(\d+)', key)
        value[0] = div[value[0]]
        value[1] = value[1].zfill(2)
        value[2] = car[value[2]]
        value=''.join(value)
        rank_dict[key] = value

    df['r1_sort_rank'] = df['rikishi1_rank'].map(rank_dict)


    df_sorted = df.sort_values(by=['r1_sort_rank'])
    sort_list = df_sorted['r1_sort_rank'].unique().tolist()
    ordinal_rank = {}
    for rank in sort_list:
        ordinal_rank[rank] = sort_list.index(rank)+1
        
    df['r1_ord_rank'] = df['r1_sort_rank'].map(ordinal_rank)

    return df

def prior_record(df):
    """    
    Creates "r1_prior_wins" and "r1_prior_losses" that gives the prior record before the match
    """
    #Split basho to year and 'trny' columns, make day int type
    df['year'] = df['basho'].astype(str).str.split('.').str[0]
    df['trny'] = df['basho'].astype(str).str.split('.').str[1]
    df['day'] = df['day'].astype(str).astype(int)

    #sort by col
    col = ['basho', 'rikishi1_id', 'year', 'trny', 'day']
    df = df.sort_values(col)

    def process_result(result):
        if result[0] == '(' :
            result = re.sub(r'[()]', '', result)
        else:
            result = re.split(r"\(", result)[0]
    
        return result
    
    df['r1_prior_record'] = df['rikishi1_result'].apply(process_result)

    df['r1_prior_wins'] = df['r1_prior_record'].astype(str).str.split('-').str[0].astype(int) - df['rikishi1_win'].astype(int)
    df['r1_prior_losses'] = df['r1_prior_record'].astype(str).str.split('-').str[1].astype(int) - df['rikishi2_win'].astype(int)
    df['prior_record'] = df['r1_prior_wins'].astype(str)+'-'+df['r1_prior_losses'].astype(str)

    return df
# This function adds  column which tells us if a given player has 7 wins on the 14th day of a tournament. (We get None for non-penultimate days.)

def add_col_for_penultimate_day_7_wins(datfram):

    # Define the function to calculate wins
    def calculate_wins(result):
        # Initialize wins with None
        wins = None
        
        # Ensure result has at least three elements for safe indexing
        if len(result) < 3:
            return wins

        # Check if the result starts with '(' and matches other conditions
        if result[0] == '(':
            if result[2] != '-':
                wins = result[1] + result[2]  # Concatenate first and second characters if second character is '0'
            elif result[1].isdigit() and int(result[1]) < 10:
                wins = result[1]  # If result[1] is a single digit, assign it to wins as an integer

        # Check alternative conditions if not wrapped in parentheses
        elif result[1] != '-':
            wins = result[0] + result[1]
        elif result[0].isdigit() and int(result[0]) < 10:
            wins = int(result[0])

        return wins

    # Apply the function to each row in 'rikishi1_result' and create the new column
    datfram['rikishi1_wins_in_tournament'] = datfram['rikishi1_result'].apply(calculate_wins)
    datfram['rikishi2_wins_in_tournament'] = datfram['rikishi2_result'].apply(calculate_wins)


    datfram['rikishi1_penultimate_day_7_wins'] = None
    datfram['rikishi2_penultimate_day_7_wins'] = None

    for i in range(datfram.shape[0]):
        if datfram['day'][i] == 14:
            if datfram['rikishi1_wins_in_tournament'][i] == 7:
                datfram.loc[i,'rikishi1_penultimate_day_7_wins'] = True
            if datfram['rikishi1_wins_in_tournament'][i] != 7:
                datfram.loc[i,'rikishi1_penultimate_day_7_wins'] = False

            if datfram['rikishi2_wins_in_tournament'][i] == 7:
                datfram.loc[i,'rikishi2_penultimate_day_7_wins'] = True
            if datfram['rikishi2_wins_in_tournament'][i] != 7:
                datfram.loc[i,'rikishi2_penultimate_day_7_wins'] = False
    
    return datfram



# This function adds a column that tells us how long a given player has been in sumo.

def get_how_long_in_sumo(datfram):
    # Make a column for year.
    datfram['year'] = datfram['basho'].astype(str).str.split('.').str[0].astype(int)

    # Sort by year.
    datfram = datfram.sort_values(by=['year'])

    # Find the first appearance year for each rikishi id.
    first_appearance_1 = datfram.groupby('rikishi1_id')['year'].transform('min')
    first_appearance_2 = datfram.groupby('rikishi2_id')['year'].transform('min')

    # Calculate years since first appearance (inclusive) and add this column to the df.
    datfram['rikishi1_years_in_sumo'] = datfram['year'] - first_appearance_1 + 1
    datfram['rikishi2_years_in_sumo'] = datfram['year'] - first_appearance_2 + 1

    return datfram
