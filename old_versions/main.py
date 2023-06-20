import openai
import sys
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

messages = [{"role": "system", "content": '''
You are a chess AI, you will receive a chess board. You are the uppercase pieces (black pieces) and your opponent the lowercase pieces (white pieces), you will play by replying with a move of four chars with the source piece and the dist position like "e4e4".
'''}]

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

def board_text(board):
    text = '   a b c d e f g h\n\n'
    for row_index, row in enumerate(board):
        text += f'{len(board) - row_index}  '
        for piece_index, piece in enumerate(row):
            text += f'{piece} '
        text += '\n'
    return text

def is_valid_move(move, board):
    if len(move) != 4:
        return False
        
    move = move.lower()

    source_column, source_row = positions[move[0]], 8 - int(move[1])
    dest_column, dest_row = positions[move[2]], 8 - int(move[3])

    if not (0 <= source_column < 8) or not (0 <= source_row < 8) or not (0 <= dest_column < 8) or not (0 <= dest_row < 8):
        return False

    piece = board[source_row][source_column]

    if piece == '.' or (piece.islower() and turn == 'upper') or (piece.isupper() and turn == 'lower'):
        return False

    if piece.lower() == 'p':
        if source_column == dest_column:
            if piece.isupper():
                if source_row - dest_row == 1:
                    return True
                elif source_row == 6 and source_row - dest_row == 2 and board[5][source_column] == '.':
                    return True
            else:
                if dest_row - source_row == 1:
                    return True
                elif source_row == 1 and dest_row - source_row == 2 and board[2][source_column] == '.':
                    return True
        elif abs(source_column - dest_column) == 1 and abs(source_row - dest_row) == 1:
            dest_piece = board[dest_row][dest_column]
            if dest_piece != '.' and dest_piece.islower() != piece.islower():
                return True
    elif piece.lower() == 'r':
        if source_column == dest_column or source_row == dest_row:
            return True
    elif piece.lower() == 'n':
        if (abs(source_column - dest_column) == 2 and abs(source_row - dest_row) == 1) or (abs(source_column - dest_column) == 1 and abs(source_row - dest_row) == 2):
            dest_piece = board[dest_row][dest_column]
            if dest_piece == '.' or dest_piece.islower() != piece.islower():
                return True
    elif piece.lower() == 'b':
        if abs(source_column - dest_column) == abs(source_row - dest_row):
            return True
    elif piece.lower() == 'q':
        if source_column == dest_column or source_row == dest_row or abs(source_column - dest_column) == abs(source_row - dest_row):
            return True
    elif piece.lower() == 'k':
        if abs(source_column - dest_column) <= 1 and abs(source_row - dest_row) <= 1:
            return True

    return False


def move(move_input, board):
    source_column, source_row = positions[move_input[0]], 8 - int(move_input[1])
    dest_column, dest_row = positions[move_input[2]], 8 - int(move_input[3])

    board[dest_row][dest_column] = board[source_row][source_column]
    board[source_row][source_column] = '.'

    return board
        
def gpt_move():
    game = f'Updated chessboard:\n\n{board_text(board)}\nLast {last_turn} move: {last_move}'
    
    messages.append({"role": "user", "content": game})
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
        
    #result = re.findall(r"\['(.*?)'\]", reply)
        
    #if result:
    #    gpt_move_reply = result[0]
    #    return gpt_move_reply
    #else:
    #    gpt_move_reply = reply[-4:].replace('!', '').replace('.', '').replace('"', "''.replace("'", '').replace('m', '')
    #    if len(gpt_move_reply) == 4:
    #        return gpt_move_reply
    
    #input(reply)
                    
    return reply

turn = 'lower'

last_move = None
last_turn = None

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(board_text(board))
    
    if last_move: print(f'Last {last_turn} move: {last_move}')

    move_input = input(f'{turn.capitalize()} move: ') if turn == 'lower' else gpt_move()
    
    move_result = re.search(r"\b([a-h][1-8][a-h][1-8])\b", move_input)
    
    #input(f'Is valid move: {is_valid_move(move_input, board)}')
    
    if move_result:
        finish_move = move_result.group(1)
        
        board = move(finish_move, board)
        
        last_move = finish_move
        last_turn = turn
        
        turn = 'upper' if turn == 'lower' else 'lower'
    else:
        input(f'Invalid {turn} move input: {move_input}')

    time.sleep(0.1)
