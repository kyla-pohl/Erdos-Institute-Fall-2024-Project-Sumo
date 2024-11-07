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
