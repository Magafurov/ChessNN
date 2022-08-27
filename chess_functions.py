import chess
import chess.pgn
import numpy as np
import tensorflow as tf
import copy
import math
import re


switcher = { #based on x, y displacement without promotion options
    (1,0):0,(2,0):1,(3,0):2,(4,0):3,(5,0):4,(6,0):5,(7,0):6,(-1,0):7,(-2,0):8,(-3,0):9,(-4,0):10,(-5,0):11,(-6,0):12,(-7,0):13,(0,1):14,(0,2):15,(0,3):16,(0,4):17,(0,5):18,(0,6):19,(0,7):20,(0,-1):21,(0,-2):22,(0,-3):23,(0,-4):24,(0,-5):25,(0,-6):26,(0,-7):27,(1,1):28,(2,2):29,(3,3):30,(4,4):31,(5,5):32,(6,6):33,(7,7):34,(-1,-1):35,(-2,-2):36,(-3,-3):37,(-4,-4):38,(-5,-5):39,(-6,-6):40,(-7,-7):41,(1,-1):42,(2,-2):43,(3,-3):44,(4,-4):45,(5,-5):46,(6,-6):47,(7,-7):48,(-1,1):49,(-2,2):50,(-3,3):51,(-4,4):52,(-5,5):53,(-6,6):54,(-7,7):55,(2,1):56,(2,-1):57,(-2,1):58,(-2,-1):59,(1,2):60,(-1,2):61,(1,-2):62,(-1,-2):63,
        
    }
                 
dicV = []

for a in range(8):
    for b in range(8):  
        for tup, value in switcher.items():
            y=a+tup[0]
            x=b+tup[1]
            if 0<=x<8 and 0<=y<8:
                dicV.append(value+b*64+a*8*64)
                
                
                
                
                
"""
Takes python-chess move object and makes its coordinates as if white is black and black is white
"""
def rotmove(move):
    m=copy.deepcopy(move)
    
    m.from_square=63 - move.from_square
    m.to_square=63 - move.to_square
    
    return m
    
    
    
    
"""
Takes a move and board and outputs a (1792) tensor with all zeros and one 1 that is the actual move the player made
"""
def TargetMoveTensor(move,board):
    
    if int(board.turn)==0:
        m=rotmove(move)
    else:
        m=move
        
    MoveTensor=np.zeros((8,8,64), dtype=bool)
    diffx=chess.square_file(m.from_square)-chess.square_file(m.to_square)
    diffy=chess.square_rank(m.from_square)-chess.square_rank(m.to_square) 
   
    MoveTensor[chess.square_rank(m.to_square),
               chess.square_file(m.to_square),
               switcher.get((diffy,diffx), "nothing")]=1
    
    MoveTensor = tf.reshape(MoveTensor, [8*8*64])
    MoveTensor = tf.gather(MoveTensor, dicV, axis=-1)

    return MoveTensor
    
    



"""
Recieves python-chess board object. Outputs a tensor of dimensions (8,8,64) 
where all illegal moves are -tf.float32.max and legal moves are 0
"""
def MoveTensorLegal(board):
    MoveTensorLegal=np.full((8,8,64), 1, dtype=bool)
    
    for move in list(board.legal_moves):
        
        if int(board.turn)==0:
            m=rotmove(move)
        else:
            m=move
        
        diffx=chess.square_file(m.from_square)-chess.square_file(m.to_square)
        diffy=chess.square_rank(m.from_square)-chess.square_rank(m.to_square) 
        
        MoveTensorLegal[chess.square_rank(m.to_square),
               chess.square_file(m.to_square),
               switcher.get((diffy,diffx), "nothing")]=0
        
    MoveTensorLegal = tf.reshape(MoveTensorLegal, [8*8*64])
    MoveTensorLegal = tf.gather(MoveTensorLegal, dicV, axis=-1)

    return MoveTensorLegal
    
    
    
    
    
def timefun(x,a,b):
    assert b>a
    if x<=a:
        return 0
    elif a<x<b:
        return (x-a)/(b-a)
    else:
        return 1


"""
Recieves python-chess board object and ouputs (8,8,102) tensor 
that contains all the information needed for the neural network
"""
    
def split_dims(
        board,
        timelist=False, # removes time information
        giventime=900,
        increment=10,
        myT=900,
        enT=900,
        myelo=1800,
        hiselo=1800,
        rem_context=False): # removes past move information
    

    board3d = np.zeros((8, 8, 72), dtype=bool)
    float_arr = np.zeros((34), dtype=np.float32)
    bor=board.copy()   

    for piece in chess.PIECE_TYPES: # antagonist's pieces current
        for square in bor.pieces(piece, not board.turn):
            idx = np.unravel_index(square, (8, 8))
            board3d[idx[0]][idx[1]][0 + piece - 1] = 1

    for piece in chess.PIECE_TYPES: # protagonist's pieces current
        for square in bor.pieces(piece, board.turn):
            idx = np.unravel_index(square, (8, 8))
            board3d[idx[0]][idx[1]][6 + piece - 1] = 1
    
    
    if rem_context==False: # removes past move information
        
        q = not board.turn
        for t in range(10):

            try:
                bor.pop()
                
                for piece in chess.PIECE_TYPES:
                    for square in bor.pieces(piece, q):
                        idx = np.unravel_index(square, (8, 8))
                        board3d[idx[0]][idx[1]][12 + t*6 + piece - 1] = 1
                
                if timelist is not False:
                    float_arr[t]=timefun(timelist[-(t+1)],0,300)
                    
                q = not q
                
            except:
                float_arr[10+t] = 1
            
    else:
        float_arr[10:20] = 1

                 
    if int(board.turn)==0:
        for i in range(board3d.shape[2]):
            board3d[:,:,i]=np.rot90((board3d[:,:,i]),2)
            
            
    float_arr[20]=int(board.turn)
    float_arr[21]=board.has_kingside_castling_rights(board.turn)
    float_arr[22]=board.has_queenside_castling_rights(board.turn)
    float_arr[23]=board.has_kingside_castling_rights(not board.turn)
    float_arr[24]=board.has_queenside_castling_rights(not board.turn)
    
    float_arr[25]=timefun(myelo,1400,2600)
    float_arr[26]=timefun(hiselo,1400,2600)
    
    if timelist is not False:
        
        float_arr[27]=timefun(increment,0,30)
        float_arr[28]=timefun(giventime,0,900)
        float_arr[29]=timefun(myT,0,120)
        float_arr[30]=timefun(enT,0,120)
        float_arr[31]=timefun(myT,0,900)
        float_arr[32]=timefun(enT,0,900)

    else:
        float_arr[33]=1
        

    
    return board3d, float_arr




def TopN(arch,num,model,nmoves): #testing based on npz file // model does not predict time // takes in elo&time
    i=0      

    x_bool_arch  = arch['arr_0']
    x_float_arch = arch['arr_1']
    b_arch       = arch['arr_2']
    y_arch       = arch['arr_3']
    
    
    for n in range(num):
    
        x_bool  = x_bool_arch[n*512:(n+1)*512]
        x_float = x_float_arch[n*512:(n+1)*512]
        b       = b_arch[n*512:(n+1)*512]
        y       = y_arch[n*512:(n+1)*512]
        
        b = tf.cast(b, dtype=tf.float32)
        b = -tf.float32.max * b

        MT = model([b, x_bool, x_float], training=False)
        MoveTensor = MT.numpy()
        MoveTensor = np.argpartition(MoveTensor, -nmoves, axis=-1)[:,-nmoves:]
        y_idx = np.argmax(y, axis=-1)          

        for batch in range(512):
            for q in range(nmoves):
                if MoveTensor[batch,q]==y_idx[batch]:
                    i+=1
                    break
                    

    return (i/(num*512))