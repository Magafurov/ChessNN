import chess
import chess.pgn
import chess_functions
import numpy as np
import re
import random
from tensorflow import reshape,gather

def f(x):
    return x*x
    
def job(num):
    return num * 2
    
def helper_process_game(games):

    x_bool_train = []
    x_float_train = []
    ytrain= []
    btrain = []
    timetaken = []
    boards=[]            

    for game in games:

        board = chess.Board()
        Welo=int(game.headers["WhiteElo"])
        Belo=int(game.headers["BlackElo"])
        tc = game.headers["TimeControl"]
        
        giventime, increment = re.split(r"\+", tc)
        giventime = float(giventime)
        increment = float(increment)

        WT=giventime
        BT=giventime
        localtt=[]
                    
        for node in game.mainline():
                       
            if np.random.random(1)[0]<0.95: # remove all time data
                simplify=False
            else: 
                simplify=True
                                        
            if np.random.random(1)[0]<0.98: # remove all past move data
                rem_context=False
            else: 
                rem_context=True
                
            try:
                clock=float(node.clock())
            except:
                print("clock error")
                break
                                
            if board.turn==True:
                myelo=Welo
                hiselo=Belo
                myT=clock
                enT=BT
                movetime = WT - clock + increment
                WT = clock

            else:
                myelo=Belo
                hiselo=Welo
                myT=clock
                enT=WT
                movetime = BT - clock + increment
                BT = clock
                
            localtt.append(movetime)
            
            if simplify:
                x_bool, x_float = chess_functions.split_dims(board,
                myelo=myelo,
                hiselo=hiselo,
                rem_context=rem_context)
            else:
                x_bool, x_float = chess_functions.split_dims(board,
                timelist=localtt[-11:-1],
                giventime=giventime,
                increment=increment,
                myT=myT,
                enT=enT,
                myelo=myelo,
                hiselo=hiselo,
                rem_context=rem_context)  
 
            
            x_bool_train.append(x_bool)
            x_float_train.append(x_float)
            
            ytrain.append(chess_functions.TargetMoveTensor(node.move,board))
            btrain.append(chess_functions.MoveTensorLegal(board))
            timetaken.append(movetime)
            boards.append(board.copy())

            board.push(node.move)
        
    #final = zip(xtrain, ytrain, btrain, timetaken, boards) 
    return x_bool_train, x_float_train, ytrain, btrain, timetaken, boards