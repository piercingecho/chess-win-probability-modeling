import pandas as pd
from statistics import fmean

def buildChessDataframePerMove(df_x : pd.DataFrame, series_y: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
    '''
    Takes a dataframe where every row represents a chess game, and a series where every value represents whether the corresponding
    row was a win or loss.

    Outputs a new dataframe and series where every row represents a move in a chess game. Utilizes a multiindex, unique id and GameID, where 
    the original dataframe's game is referenced.

    df_x MUST have the following columns: ['whiteElo', 'blackElo', 'StockfishScores', 'StockfishDeltas']
    '''
    x_columns = ["GameId",
                 "WhiteElo", 
                 "BlackElo", 
                 "EloDifference",
                 "MoveNumber", 
                 "WhiteTurn", 
                 "CurrentStockfishScore", 
                 "WhiteAverageDelta", 
                 "BlackAverageDelta",
                 "MoveNum*StockfishScore",
                 "MoveNum*WhiteAvgDelta",
                 "MoveNum*BlackAvgDelta"]

    new_data_x = []

    new_data_y = []

    a = False


    row_number = 0

    # for multiindexing y
    game_id_list = []
    move_num_list = []

    for index, row in df_x.iterrows():

        y_value = series_y[index]

        is_white_turn = True
        scores = row['StockfishScores'].split(" ")

        currScore = 0
        for j in range(len(scores)):
            if(scores[j] == 'NA'):
                scores[j] = currScore
            else:
                scores[j] = int(scores[j])
                currScore = scores[j]

        deltas = row['StockfishDeltas'].split(" ")
        for j in range(len(deltas)):
            deltas[j] = int(deltas[j])


        for move_number in range(1, len(scores) + 1):
            new_x_row = {}

            new_x_row["GameId"] = index

            new_x_row['WhiteElo'] = row['WhiteElo']
            new_x_row['BlackElo'] = row['BlackElo']
            new_x_row['EloDifference'] = row['WhiteElo'] - row['BlackElo']
            new_x_row['MoveNumber'] = move_number

            new_x_row['WhiteTurn'] = 1 if is_white_turn else 0

            curr_stockfish_score = scores[move_number - 1]
            new_x_row['CurrentStockfishScore'] = curr_stockfish_score


            white_avg_delta = findAverageDelta(deltas, move_number, is_white = True)
            black_avg_delta = findAverageDelta(deltas, move_number, is_white = False)

            new_x_row['WhiteAverageDelta'] = white_avg_delta
            new_x_row['BlackAverageDelta'] = black_avg_delta


            ### Interaction terms

            new_x_row["MoveNum*StockfishScore"] = move_number * curr_stockfish_score
            new_x_row["MoveNum*WhiteAvgDelta"] = move_number * white_avg_delta
            new_x_row["MoveNum*BlackAvgDelta"] = move_number * black_avg_delta
            


            new_data_x.append(buildOrderedListFromDictionary(new_x_row, x_columns))
            new_data_y.append(y_value)

            game_id_list.append(index)
            move_num_list.append(move_number)


            is_white_turn = not is_white_turn # alternate between white and black
        


    new_df_x = pd.DataFrame(new_data_x, columns = x_columns)
    new_df_x.set_index(["GameId"], inplace=True,
             append=True)
    
    new_series_y = pd.Series(new_data_y, index=pd.MultiIndex.from_arrays([game_id_list, move_num_list], names=['Game ID', 'Move Number']))

    return new_df_x, new_series_y


def buildOrderedListFromDictionary(values : dict[str, str], column_order: list[str]):
    '''
    Builds a 1-d list from the dictionary, in the order of the values in column order.
    '''
    new_list = []
    for name in column_order:
        new_list.append(values[name])
    
    return new_list

def findAverageDelta(deltas: list[int], move_number: int, is_white: bool) -> float:
    '''
    Returns the average stockfish delta from the move number.

    Parameters:
    deltas: the list of deltas for both white and black moves.
    
    move_number: the move number to stop at. 1 will use only white's first move, 2 will use white's first and black's 
      first move, etc.
    
    is_white: calculates white's average delta if true, otherwise calculates black's.

    Returns:

    float: the average stockfish delta that white/black had up to this point in the game. 
    '''

    # Use every other move. For white, start at index 0; for black, index 1. Go till the current move number
    list_to_average = deltas[0 + int(not(is_white)):move_number:2]


    if(len(list_to_average) == 0):
        return 0
    else:
        return (sum(list_to_average) / len(list_to_average))