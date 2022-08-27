from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
import random
import copy

import net

#engine = chess.engine.SimpleEngine.popen_uci(
#    r"C:\Users\ti-ho\Documents\stockfish_15_win_x64_avx2\stockfish_15_x64_avx2.exe")


app = Flask(__name__)

cors = CORS(app)

board = chess.Board()
elo = 1800

def stockfish_engine(board):
    l=[]

    for move in list(board.legal_moves):
        b = board.copy()
        b.push(move)
        l.append(engine.analyse(b, chess.engine.Limit(time=0.001))['score'].white().score(mate_score=10000))
        
    #print(l)
    return list(board.legal_moves)[l.index(max(l))]







# data looks like {'color': 'w', 'from': 'd7', 'to': 'd8',
# 'flags': 'np', 'piece': 'p', 'promotion': 'q', 'san': 'd8=Q+'}

#Create the receiver API POST endpoint:
@app.route("/receiver", methods=["POST"])
def postME():
    global board
    global elo
    data = request.get_json()
    print(type(data),data)
    
    #board = chess.Board()
    if data=="init":
        board = chess.Board()
        return jsonify('ack')
    elif data=="takeback":
        try:
            board.pop()
            board.pop()
        except:
            pass
        return jsonify('ack takeback')
    elif isinstance(data, str) and data[0:4]=="fen ":
        board = chess.Board(fen=data[4:])
        return jsonify('ack')
    elif isinstance(data, str) and data[0:4]=="elo ":
        elo = int(data[4:])
        return jsonify('ack elo '+str(elo))
    else:
        input_move = board.parse_san(data['san'])

        if input_move in list(board.legal_moves):
            board.push(input_move)
            print("Input move: ",input_move)
        else:
            print("Illegal move: ", input_move)
            print(list(board.legal_moves))
        
        
        if len(list(board.legal_moves))>0:
            #output_move = random.choice(list(board.legal_moves))
            
            output_move = net.process_board(board, elo)
            #output_move = stockfish_engine(board)
            
            print(output_move)
            
            san_output_move = board.san(output_move)
            
            board.push(output_move)
            
            data = jsonify(san_output_move)
            
            print("Output move: ", san_output_move)
            
            return data
        else:
            return jsonify("game_ended")
   
if __name__ == "__main__": 
    app.run(debug=True)
