import chess
import pygame
import openai
import os
import time
import re
import time
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
gpt_model = os.getenv('GPT_MODEL')

messages = [{"role": "system", "content": 'You are a chess AI, you are the black pieces, you will play by replying with a move of four chars with the source piece and the dist position like "e4e4".'}]

pieces = {
    'p': 'pawn',
    'r': 'rook',
    'n': 'knight',
    'b': 'bishop',
    'q': 'queen',
    'k': 'king'
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
    '.': 'empty'
}

positions = {
    '0': 'a',
    '1': 'b',
    '2': 'c',
    '3': 'd',
    '4': 'e',
    '5': 'f',
    '6': 'g',
    '7': 'h',
}

board = chess.Board()

array_board = str(board).split('\n')

for i, x in enumerate(array_board):
    array_board[i] = x.split()
    
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

turn = 'white'

selected_piece = None
selected_pos = None

last_move = None
last_turn = None

checkmate = False
slatemate = False

def move(finish_move):
    global last_turn
    global last_move
    global array_board
    global turn
    global array_board
    global selected_piece
    global selected_pos
    global board
        
    board.push_san(finish_move)
                
    last_move = finish_move
    last_turn = turn
                            
    turn = 'white' if turn == 'black' else 'black'
                            
    selected_pos = None
    selected_piece = None
                            
    array_board = str(board).split('\n')

    for i, x in enumerate(array_board):
        array_board[i] = x.split()

def gpt_move():
    last_move_source_piece, last_move_dest_piece = last_move[0]+last_move[1], last_move[2]+last_move[3]
    last_move_source_piece_at, last_move_dest_piece_at = board.piece_at(chess.parse_square(last_move_source_piece)), board.piece_at(chess.parse_square(last_move_dest_piece))
    if not last_move_source_piece_at: last_move_source_piece_at = '.'
    if not last_move_dest_piece_at: last_move_dest_piece_at = '.'
    last_move_source_piece_name, last_move_dest_piece_name = pieces_names[str(last_move_source_piece_at)], pieces_names[str(last_move_dest_piece_at)]
    
    message = f'Last white pieces move: {last_move}, now {last_move_source_piece} is {last_move_source_piece_name} and {last_move_dest_piece} is {last_move_dest_piece_name}.\n\nUpdated board:\n\n{board_text()}'
    #print(message)

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
                    
    move_results = re.findall(r"\b([a-h][1-8][a-h][1-8])\b", reply)
        
    if not len(move_results) == 0:
        finish_move = move_results[-1]
        
        if chess.Move.from_uci(finish_move) in board.legal_moves:
            move(finish_move)
        else:
            #print(f'Invalid {turn} move: {reply}')
            source_piece, dest_piece = finish_move[0]+finish_move[1], finish_move[2]+finish_move[3]
            source_piece_at, dest_piece_at = board.piece_at(chess.parse_square(source_piece)), board.piece_at(chess.parse_square(dest_piece))
            if not source_piece_at: source_piece_at = '.'
            if not dest_piece_at: dest_piece_at = '.'
            source_piece_name, dest_piece_name = pieces_names[str(source_piece_at)], pieces_names[str(dest_piece_at)]
                        
            message = f'{finish_move} is not a valid move, {source_piece} is {source_piece_name} and {dest_piece} is {dest_piece_name}, please do valid moves.'
            #print(message)
            
            messages.append({"role": "user", "content": message})
            time.sleep(0.1)
            gpt_move()
    else:
        #print(f'Invalid {turn} move input: {reply}')
        messages.append({"role": "user", "content": 'Please just reply with a move of four chars with the source piece and the dist position like "e4e4".'})
        gpt_move()
    
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('ChessGPT')
clock = pygame.time.Clock()
running = True
dt = 0
    
while running:
    if board.is_checkmate():
        input('Checkmate!')
        running = False
        break
    
    if board.is_stalemate(): 
        input('Slatemate!')
        running = False
    
    if board.is_insufficient_material(): 
        input('Insufficient material!')
        running = False
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                clicked_x = x // 50
                clicked_y = y // 50
                 
                clicked_piece = array_board[clicked_y][clicked_x]
                               
                if selected_piece == None:
                    if clicked_piece != '.':
                        if turn == 'black' and clicked_piece.islower():
                            selected_piece = [clicked_x, clicked_y]
                            selected_pos = f'{positions[str(clicked_x)]}{8-clicked_y}'
                        elif turn == 'white' and clicked_piece.isupper():
                            selected_piece = [clicked_x, clicked_y]
                            selected_pos = f'{positions[str(clicked_x)]}{8-clicked_y}'
                else:
                    if turn == 'black' and clicked_piece.islower():
                        selected_piece = [clicked_x, clicked_y]
                        selected_pos = f'{positions[str(clicked_x)]}{8-clicked_y}'
                    elif turn == 'white' and clicked_piece.isupper():
                        selected_piece = [clicked_x, clicked_y]
                        selected_pos = f'{positions[str(clicked_x)]}{8-clicked_y}'
                    else:
                        dis_pos = f'{positions[str(clicked_x)]}{8-clicked_y}'
                        
                        finish_move = f'{selected_pos}{dis_pos}'
                       
                        if chess.Move.from_uci(finish_move) in board.legal_moves:                
                            move(finish_move)
                                
                            if turn == 'black': gpt_move()

    screen.fill("white")
    
    for row_index, row in enumerate(array_board):
        for piece_index, piece in enumerate(row):
            color = (255, 255, 255)
            if (piece_index % 2 == 0 and row_index % 2 == 0) or (piece_index % 2 != 0 and row_index % 2 != 0): 
                color = (0, 0, 0)
            pygame.draw.rect(screen, color, (50*piece_index, 50*row_index, 50, 50))
            if piece != '.': 
                if piece.isupper(): 
                    screen.blit(pygame.transform.scale(pygame.image.load(f"pieces/{pieces[piece.lower()]}.png"), (50, 50)), (50*piece_index, 50*row_index))
                elif piece.islower():
                    image_rgba = pygame.image.load(f"pieces/{pieces[piece]}.png").convert_alpha()
                    image_data = pygame.image.tostring(image_rgba, "RGBA")
                    pil_image = Image.frombytes("RGBA", image_rgba.get_size(), image_data)
                    pixels = pil_image.load()
                    width, height = pil_image.size
                    for x2 in range(width):
                        for y2 in range(height):
                            r, g, b, a = pixels[x2, y2]
                            new_r, new_g, new_b = 255 - r, 255 - g, 255 - b
                            pixels[x2, y2] = new_r, new_g, new_b, a
                    inverted_image_data = pil_image.tobytes()
                    inverted_image = pygame.image.fromstring(inverted_image_data, pil_image.size, "RGBA")
                    screen.blit(pygame.transform.scale(inverted_image, (50, 50)), (50*piece_index, 50*row_index))
                 
    if selected_piece is not None:
        pygame.draw.rect(screen, (0, 175, 0), (50 * selected_piece[0], 50 * selected_piece[1], 50, 50), 3)
    
    pygame.display.flip()
    dt = clock.tick(10) / 1000
    
pygame.quit()