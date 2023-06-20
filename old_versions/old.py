import pygame, openai, os, re
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

messages = [
    {"role": "system", "content": "You are a chess artificial intelligence, you are the black pieces, you will receive an array from the board and return an array with the position of the black piece you chose and the other position where you want it to move, for example [3, 6, 3, 7], the format would be [from_x, from_y, to_x, to_y], Move the piece that you think is most convenient."}
]

board = [
    ['black_rook','black_knight','black_bishop','black_queen','black_king','black_knight','black_knight','black_rook'],
    ['black_pawn','black_pawn','black_pawn','black_pawn','black_pawn','black_pawn','black_pawn','black_pawn'],
    [None,None,None,None,None,None,None,None],
    [None,None,None,None,None,None,None,None],
    [None,None,None,None,None,None,None,None],
    [None,None,None,None,None,None,None,None],
    ['white_pawn','white_pawn','white_pawn','white_pawn','white_pawn','white_pawn','white_pawn','white_pawn'],
    ['white_rook','white_knight','white_bishop','white_queen','white_king','white_knight','white_knight','white_rook']
]

selected_piece = None

def move(from_x, from_y, to_x, to_y):
    piece = board[from_y][from_x]
    if piece is None:
        return False
        
    valid_moves = get_valid_moves(piece, from_x, from_y)

    if (to_x, to_y) in valid_moves:
        board[to_y][to_x] = piece
        board[from_y][from_x] = None
        return True

    return False
        
def gpt_move():
    print('gtp_move')
    messages.append({"role": "user", "content": str(board)})
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    reply = chat.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    
    matches = re.findall(r"\[\d,\d,\d,\d\]", re.sub(r"[^\d\[\],]", "", reply))
    four_positions_arrays = []

    for match in matches:
        extracted_array = eval(match)
        if len(extracted_array) == 4:
            four_positions_arrays.append(extracted_array)

    if four_positions_arrays:
        moved = move(*four_positions_arrays[0])
        if moved:
            print("GPT moved:", four_positions_arrays[0])
        else:
            print("GPT invalid moved:", four_positions_arrays[0])
            messages.append({"role": "user", "content": "Please make valid moves."})
            gpt_move()
    else:
        print("No four positions arrays found.")
    
def get_valid_moves(piece, x, y):
    if piece == 'white_pawn':
        return get_valid_moves_white_pawn(x, y)
    elif piece == 'black_pawn':
        return get_valid_moves_black_pawn(x, y)
    elif piece == 'white_rook':
        return get_valid_moves_rook(x, y)
    elif piece == 'black_rook':
        return get_valid_moves_rook(x, y)
    elif piece == 'white_knight':
        return get_valid_moves_knight(x, y)
    elif piece == 'black_knight':
        return get_valid_moves_knight(x, y)
    elif piece == 'white_bishop':
        return get_valid_moves_bishop(x, y)
    elif piece == 'black_bishop':
        return get_valid_moves_bishop(x, y)
    elif piece == 'white_queen':
        return get_valid_moves_queen(x, y)
    elif piece == 'black_queen':
        return get_valid_moves_queen(x, y)
    elif piece == 'white_king':
        return get_valid_moves_king(x, y)
    elif piece == 'black_king':
        return get_valid_moves_king(x, y)

    return []

def get_valid_moves_white_pawn(x, y):
    valid_moves = []

    if y > 0 and board[y - 1][x] is None:
        valid_moves.append((x, y - 1))

    if y == 6 and board[y - 1][x] is None and board[y - 2][x] is None:
        valid_moves.append((x, y - 2))

    if y > 0 and x > 0 and board[y - 1][x - 1] is not None and board[y - 1][x - 1].startswith('black_'):
        valid_moves.append((x - 1, y - 1))

    if y > 0 and x < 7 and board[y - 1][x + 1] is not None and board[y - 1][x + 1].startswith('black_'):
        valid_moves.append((x + 1, y - 1))

    return valid_moves

def get_valid_moves_black_pawn(x, y):
    valid_moves = []

    if y < 7 and board[y + 1][x] is None:
        valid_moves.append((x, y + 1))

    if y == 1 and board[y + 1][x] is None and board[y + 2][x] is None:
        valid_moves.append((x, y + 2))

    if y < 7 and x > 0 and board[y + 1][x - 1] is not None and board[y + 1][x - 1].startswith('white_'):
        valid_moves.append((x - 1, y + 1))

    if y < 7 and x < 7 and board[y + 1][x + 1] is not None and board[y + 1][x + 1].startswith('white_'):
        valid_moves.append((x + 1, y + 1))

    return valid_moves

def get_valid_moves_rook(x, y):
    valid_moves = []

    # Vertical moves
    for i in range(y - 1, -1, -1):
        if board[i][x] is None:
            valid_moves.append((x, i))
        else:
            if board[i][x].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((x, i))
            break

    for i in range(y + 1, 8):
        if board[i][x] is None:
            valid_moves.append((x, i))
        else:
            if board[i][x].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((x, i))
            break

    # Horizontal moves
    for i in range(x - 1, -1, -1):
        if board[y][i] is None:
            valid_moves.append((i, y))
        else:
            if board[y][i].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((i, y))
            break

    for i in range(x + 1, 8):
        if board[y][i] is None:
            valid_moves.append((i, y))
        else:
            if board[y][i].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((i, y))
            break

    return valid_moves

def get_valid_moves_knight(x, y):
    valid_moves = []

    knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    for move in knight_moves:
        new_x = x + move[0]
        new_y = y + move[1]
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            if board[new_y][new_x] is None or board[new_y][new_x].startswith('white_'):
                valid_moves.append((new_x, new_y))

    return valid_moves

def get_valid_moves_bishop(x, y):
    valid_moves = []

    # Top-left to bottom-right diagonal
    i = 1
    while x - i >= 0 and y - i >= 0:
        if board[y - i][x - i] is None:
            valid_moves.append((x - i, y - i))
        else:
            if board[y - i][x - i].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((x - i, y - i))
            break
        i += 1

    i = 1
    while x + i < 8 and y + i < 8:
        if board[y + i][x + i] is None:
            valid_moves.append((x + i, y + i))
        else:
            if board[y + i][x + i].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((x + i, y + i))
            break
        i += 1

    # Top-right to bottom-left diagonal
    i = 1
    while x + i < 8 and y - i >= 0:
        if board[y - i][x + i] is None:
            valid_moves.append((x + i, y - i))
        else:
            if board[y - i][x + i].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((x + i, y - i))
            break
        i += 1

    i = 1
    while x - i >= 0 and y + i < 8:
        if board[y + i][x - i] is None:
            valid_moves.append((x - i, y + i))
        else:
            if board[y + i][x - i].startswith('white_') and board[y][x].startswith('black_'):
                valid_moves.append((x - i, y + i))
            break
        i += 1

    return valid_moves

def get_valid_moves_queen(x, y):
    valid_moves = []

    valid_moves.extend(get_valid_moves_rook(x, y))
    valid_moves.extend(get_valid_moves_bishop(x, y))

    return valid_moves

def get_valid_moves_king(x, y):
    valid_moves = []

    king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for move in king_moves:
        new_x = x + move[0]
        new_y = y + move[1]
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            if board[new_y][new_x] is None or board[new_y][new_x].startswith('white_'):
                valid_moves.append((new_x, new_y))

    return valid_moves

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('ChessGPT')
clock = pygame.time.Clock()
running = True
dt = 0

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    clicked_x = x // 50
                    clicked_y = y // 50
                    if selected_piece is None:
                        selected_piece = (clicked_x, clicked_y)
                    else:
                        moved = move(selected_piece[0], selected_piece[1], clicked_x, clicked_y)
                        if moved:
                            print("Player moved:", selected_piece, "->", (clicked_x, clicked_y))
                            gpt_move()
                        selected_piece = None

        screen.fill("white")
        
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                color = (255, 255, 255)
                if (x % 2 == 0 and y % 2 == 0) or (x % 2 != 0 and y % 2 != 0): color = (0, 0, 0)
                pygame.draw.rect(screen, color, (50*x, 50*y, 50, 50))
                if piece: 
                    if piece.startswith('white_'): screen.blit(pygame.transform.scale(pygame.image.load(f"pieces/{piece.removeprefix('white_')}.png"), (50, 50)), (50*x, 50*y))
                    elif piece.startswith('black_'):
                        image_rgba = pygame.image.load(f"pieces/{piece.removeprefix('black_')}.png").convert_alpha()
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
                        screen.blit(pygame.transform.scale(inverted_image, (50, 50)), (50*x, 50*y))

        if selected_piece is not None:
            pygame.draw.rect(screen, (0, 255, 0), (50 * selected_piece[0], 50 * selected_piece[1], 50, 50), 3)
        
        pygame.display.flip()
        dt = clock.tick(30) / 1000

    pygame.quit()
except Exception as e:
    input(f'ERROR: {e}')