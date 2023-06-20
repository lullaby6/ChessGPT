import pygame, openai, os, re
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

messages = [{"role": "system", "content": '''
you are a chess player, you will receive a chess board in the form of a python list, and you are the uppercase pieces and your opponent the lowercase pieces and you can only make legal moves of the uppercase pieces, you will play by returning an array like [from_y, from_x, to_y, to_x].
'''}]

pieces = {
    'p': 'white_pawn',
    'r': 'white_rook',
    'n': 'white_knight',
    'b': 'white_bishop',
    'q': 'white_queen',
    'k': 'white_king',
    'P': 'black_pawn',
    'R': 'black_rook',
    'N': 'black_knight',
    'B': 'black_bishop',
    'Q': 'black_queen',
    'K': 'black_king',
}

board = [
    ['R','N','B','Q','K','B','N','R'],
    ['P','P','P','P','P','P','P','P'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['.','.','.','.','.','.','.','.'],
    ['p','p','p','p','p','p','p','p'],
    ['r','n','b','q','k','b','n','r']
]

turn = 'white'

selected_piece = None

def move(from_x, from_y, to_x, to_y):
    global selected_piece
    global turn
    global board
    
    board[to_x][to_y] = board[from_x][from_y]
    board[from_x][from_y] = '.'
    
    return True

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
        # moved = move(four_positions_arrays[0][1], four_positions_arrays[0][0], four_positions_arrays[0][3], four_positions_arrays[0][2])
        if moved:
            print("GPT moved:", four_positions_arrays[0])
        else:
            print("GPT invalid moved:", reply)
            # messages.append({"role": "user", "content": f"{four_positions_arrays[0]} is not a valid move, please try again."})
            # gpt_move()
    else:
        print("No four positions arrays found.", reply)

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption('ChessGPT')
clock = pygame.time.Clock()
running = True
dt = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                clicked_x = x // 50
                clicked_y = y // 50
                    
                clicked_piece = board[clicked_y][clicked_x]
                    
                print(clicked_y, clicked_x)
                
                if selected_piece == None:
                    if clicked_piece != '.':
                        if turn == 'white' and clicked_piece.islower():
                            selected_piece = [clicked_x, clicked_y]
                        elif turn == 'black' and clicked_piece.isupper():
                            selected_piece = [clicked_x, clicked_y]
                else:
                    moved = None
                    
                    if turn == 'white' and clicked_piece.islower():
                        selected_piece = [clicked_x, clicked_y]
                    elif turn == 'black' and clicked_piece.isupper():
                        selected_piece = [clicked_x, clicked_y]
                    else:
                        moved = move(selected_piece[1], selected_piece[0], clicked_y, clicked_x)
                        
                    if moved:
                        selected_piece = None
                        gpt_move()
                        # if turn == 'white': turn = 'black'
                        # else: turn = 'white'
                    
    screen.fill("white")
        
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            color = (255, 255, 255)
            if (x % 2 == 0 and y % 2 == 0) or (x % 2 != 0 and y % 2 != 0): 
                color = (0, 0, 0)
            pygame.draw.rect(screen, color, (50*x, 50*y, 50, 50))
            if piece != '.': 
                if piece.islower(): 
                    screen.blit(pygame.transform.scale(pygame.image.load(f"pieces/{pieces[piece].removeprefix('white_')}.png"), (50, 50)), (50*x, 50*y))
                elif piece.isupper():
                    image_rgba = pygame.image.load(f"pieces/{pieces[piece].removeprefix('black_')}.png").convert_alpha()
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
    dt = clock.tick(60) / 1000

pygame.quit()