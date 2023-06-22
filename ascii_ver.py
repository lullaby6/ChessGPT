import chess 
import openai
import os
import time
import re
from dotenv import load_dotenv

load_dotenv()

os.system('mode con cols=25 lines=15')
os.system('title ChessGPT')

openai.api_key = os.getenv('OPENAI_API_KEY')
gpt_model = os.getenv('GPT_MODEL')

messages = [{"role": "system", "content": 'You are a chess AI, you are the black pieces, you will play by replying with a move of four chars with the source piece and the dist position like "e4e4".'}]

board = chess.Board()

turn = 'upper'

real_turn = {
    'lower': 'black',
    'upper': 'white'
}

pieces_names = {
    'p': 'Black Pawn',
    'r': 'Black Rook',
    'n': 'Black Knight',
    'b': 'Black bishop',
    'q': 'Black Queen',
    'k': 'Black King',
    'P': 'White Pawn',
    'R': 'White Rook',
    'N': 'White Knight',
    'B': 'White bishop',
    'Q': 'White Queen',
    'K': 'White King',
    '.': 'Empty'
}

last_move = None
last_turn = None

def board_text():
    array_board = str(board).split('\n')

    for i, x in enumerate(array_board):
        array_board[i] = x.split()
        
    text = '   a b c d e f g h\n\n'
    for row_index, row in enumerate(array_board):
        text += f'{len(array_board) - row_index}  '
        for piece_index, piece in enumerate(row):
            text += f'{piece} '
        text += '\n'

    return text

def gpt_move():
    last_move_source_piece, last_move_dest_piece = last_move[0]+last_move[1], last_move[2]+last_move[3]
    last_move_source_piece_at, last_move_dest_piece_at = board.piece_at(chess.parse_square(last_move_source_piece)), board.piece_at(chess.parse_square(last_move_dest_piece))
    if not last_move_source_piece_at: last_move_source_piece_at = '.'
    if not last_move_dest_piece_at: last_move_dest_piece_at = '.'
    last_move_source_piece_name, last_move_dest_piece_name = pieces_names[str(last_move_source_piece_at)], pieces_names[str(last_move_dest_piece_at)]
    
    message = f'Last white pieces move: {last_move}, now {last_move_source_piece} is {last_move_source_piece_name} and {last_move_dest_piece} is {last_move_dest_piece_name}.\n\nUpdated board:\n\n{board_text()}'
    
    messages.append({"role": "user", "content": message})
    
    while len(messages) > 20: messages.pop(1)
        
    reply = None
    
    while not reply:
        try:
            chat = openai.ChatCompletion.create(model=gpt_model, messages=messages)
            reply = chat.choices[0].message.content
        except: 
            time.sleep(0.5)
        
    messages.append({"role": "assistant", "content": reply})
                    
    return reply

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print(f'{board_text()}')
    
    if board.is_checkmate(): 
        print('Checkmate!')
        break
    
    if board.is_stalemate(): 
        print('Slatemate!')
        break
    
    if board.is_insufficient_material(): 
        print('Insufficient material!')
        break
    
    if last_move: print(f'Last {last_turn} move: {last_move}')

    move_input = input(f'{turn.capitalize()} move: ') if turn == 'upper' else gpt_move()
    
    move_results = re.findall(r"\b([a-h][1-8][a-h][1-8])\b", move_input)
        
    if not len(move_results) == 0:
        finish_move = move_results[-1]
        
        if chess.Move.from_uci(finish_move) in board.legal_moves:
            board.push_san(finish_move)
            
            last_move = finish_move
            last_turn = turn
            
            turn = 'upper' if turn == 'lower' else 'lower'
        else:
            #input(f'Invalid {turn} move: {move_input}')
            if turn == 'lower': 
                source_piece, dest_piece = finish_move[0]+finish_move[1], finish_move[2]+finish_move[3]
                source_piece_at, dest_piece_at = board.piece_at(chess.parse_square(source_piece)), board.piece_at(chess.parse_square(dest_piece))
                if not source_piece_at: source_piece_at = '.'
                if not dest_piece_at: dest_piece_at = '.'
                source_piece_name, dest_piece_name = pieces_names[str(source_piece_at)], pieces_names[str(dest_piece_at)]
   
                message = f'{finish_move} is not a valid move, {source_piece} is {source_piece_name} and {dest_piece} is {dest_piece_name}, please do valid moves.'
                
                messages.append({"role": "user", "content": message})
    else:
        #input(f'Invalid {turn} move input: {move_input}')
        if turn == 'lower': messages.append({"role": "user", "content": 'Please just reply with a move of four chars with the source piece and the dist position like "e4e4".'})

    time.sleep(0.1)