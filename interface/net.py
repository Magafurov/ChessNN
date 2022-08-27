import chess

import numpy as np

import tensorflow as tf
#from chessfunc import split_dims, MoveTensorLegal, GetMaxMoveWithVal
from chess_functions import split_dims, MoveTensorLegal, GetMaxMoveWithVal

#model = tf.keras.models.load_model(r"D:\Chess_documents\J\modelJ2_5250.h5")
model = tf.keras.models.load_model(r"model_2_112200.h5")

def process_board(board, elo):

    x_b, x_f = split_dims(board,
        timelist=False,
        giventime=900,
        increment=10,
        myT=900,
        enT=900,
        myelo=elo,
        hiselo=elo)
                   
    x_b = tf.convert_to_tensor(x_b[np.newaxis])
    x_f = tf.convert_to_tensor(x_f[np.newaxis])
    
    b = (MoveTensorLegal(board))
    b = tf.convert_to_tensor(b[np.newaxis])
    
    b = tf.cast(b, dtype=tf.float32)
    b = -tf.float32.max * b

    #MoveVector, predicted_t = model([b,x_b,x_f], training=False)
    MoveVector = model([b,x_b,x_f], training=False)

    bestmove, val = GetMaxMoveWithVal(MoveVector[0],board)
    
    return bestmove
