import openai
import sys
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

messages = [{"role": "system", "content": 'You are a chess AI, you will receive a chess board. You are the uppercase pieces (black pieces) and your opponent the lowercase pieces (white pieces), you will play by replying with a move of four chars with the source piece and the dist position like "e4e4".'}]

board = [
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
]

positions = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7,
}

turn = 'lower'

last_move = None
last_turn = None

def board_text():
    text = '   a b c d e f g h\n\n'
    for row_index, row in enumerate(board):
        text += f'{len(board) - row_index}  '
        for piece_index, piece in enumerate(row):
            text += f'{piece} '
        text += '\n'
    return text

def move(move_input):
    source_column, source_row = positions[move_input[0]], 8 - int(move_input[1])
    dest_column, dest_row = positions[move_input[2]], 8 - int(move_input[3])

    board[dest_row][dest_column] = board[source_row][source_column]
    board[source_row][source_column] = '.'
        
def gpt_move():
    game = f'Updated chessboard:\n\n{board_text(board)}\nLast {last_turn} move: {last_move}'
    
    messages.append({"role": "user", "content": game})
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
                    
    return reply

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(board_text())
    
    if last_move: print(f'Last {last_turn} move: {last_move}')

    move_input = input(f'{turn.capitalize()} move: ') if turn == 'lower' else gpt_move()
    
    move_results = re.findall(r"\b([a-h][1-8][a-h][1-8])\b", move_input)
        
    if not len(move_results) == 0:
        finish_move = move_results[-1]
        
        move(finish_move)
        
        last_move = finish_move
        last_turn = turn
        
        turn = 'upper' if turn == 'lower' else 'lower'
    else:
        input(f'Invalid {turn} move input: {move_input}')

    time.sleep(0.1)
