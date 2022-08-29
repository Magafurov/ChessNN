# ChessNN

ChessNN is a neural network explicitly designed to play chess in a more human-like way. It was trained on a small subset of the [lichess game database](https://database.lichess.org/). The network is similar in architecture to [maia](https://arxiv.org/abs/2006.01855): It is a convolutional neural network with additional squeeze and excitation layers.

Overall, the trained network isn't terrible at chess. It plays very well in the opening (persumably in large part due to memorization) and usually makes reasonable moves in the middle-game. However, it is bad at planning ahead and occasionally fails to see even one move ahead. This is likely because (unlike all decent chess engines) there is no search implemented in favour of human-like cognition. 

I used [chessboardjs](https://github.com/oakmac/chessboardjs) and 
[chess.js](https://github.com/jhlywa/chess.js) for the browser interface

## Requirements
This code was only tested and intended for **Windows** machines. 
To use this code you have to have a python distribution installed. Additionally you need:
- python-chess
- numpy
- tensorflow
- flask
- flask_cors

To can install these with:
```
pip install tensorflow numpy chess flask flask_cors
```

## How to play

You can play against the trained network through your browser. 
To do so, run `python_backend.py` and click `main.html`

You can run `python_backend.py` through the command line with:
```
python <dir>\ChessNN\interface\python_backend.py
```
---
![Alt Text](Animation.gif)

## How to create dataset and network

The largest source of human games is the [lichess database](https://database.lichess.org/) where you can download more than 3 billion standard games. 
Processing them requires the 
[`pgn-extract`](https://www.cs.kent.ac.uk/people/staff/djb/pgn-extract/) tool in the path.

### Filter pgn

You can filter your pgn files with `filter_pgn.ipynb` according to your chosen conditions (elo range, time controls). The tags I used are in `\pgn_npz_tag_files`.

### Generating tensor database

To convert pgn files to tensors for training use `generate.ipynb`

### Training

Initializing and training of the network is done in `training.ipynb`

