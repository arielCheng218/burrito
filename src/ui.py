from chess import Board
import pygame as pg
import algorithm
import colors
import logic
from pygame.locals import *

# TODO: promotion, add sounds

# constants
BOARD_SIZE = 544
SQUARE_SIZE = int(BOARD_SIZE / 8)
SQUARE_LETTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
SQUARE_NUMBERS = [str(x) for x in range(8, 0, -1)]
SQUARE_NAMES = []
for n in SQUARE_NUMBERS:
    for char in SQUARE_LETTERS:
        SQUARE_NAMES.append(char + n)

# dictionaries
coords_to_square = {}
square_to_coords = {}
square_to_piece_name = {}
piece_name_to_square = {}
piece_name_to_piece = {}
square_to_piece = {}
piece_to_square = {}
square_to_color = {}

promoted_piece_count = 100

def display_game_view():
    pg.init()
    screen = pg.display.set_mode((BOARD_SIZE, BOARD_SIZE))
    pg.display.set_caption("Burrito Chess")
    screen.fill(colors.BLACK)
    pg.display.update()
    draw_board(screen, False)
    draw_pieces(get_square_coords_list(), screen)
    pg.display.update()

    running = True
    is_drag_piece = False
    white_to_move = True
    drag_start_square = ""
    piece = pg.Surface((1, 1))
    piece_name = ""

    global promoted_piece_count 

    while running and not logic.game_has_ended():
        if not white_to_move:
            print("before", logic.board.fen())
            (comp_move, eval) = algorithm.minimax(logic.board, 3, False)
            if comp_move == "":
                print("White won")
                break
            logic.board.push_uci(comp_move)
            from_square = comp_move[:2]
            to_square = comp_move[2:4]
            update_rep(square_to_piece[from_square], square_to_piece_name[from_square], to_square, from_square)
            handle_castling(comp_move, screen)
            handle_en_passant(comp_move)
            blit_board_and_pieces(screen, "", "")
            if handle_promotion(comp_move, square_to_piece_name[to_square], promoted_piece_count):
                promoted_piece_count += 1
            pg.display.update()
            white_to_move = True
        else:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                elif event.type == MOUSEBUTTONDOWN and white_to_move:
                    is_drag_piece = True
                    square = get_square_name(event.pos)
                    if square in square_to_piece_name:
                        # user dragged a piece
                        piece = square_to_piece[square]
                        piece_name = square_to_piece_name[square]
                        drag_start_square = square
                        blit_board_and_pieces(screen, "", drag_start_square)
                        pg.display.update()
                elif event.type == MOUSEMOTION and is_drag_piece:
                    # redraw board + pieces without dragged piece + highlight legal move squares
                    blit_board_and_pieces(screen, piece_name, drag_start_square)
                    # overlay dragged piece
                    screen.blit(piece, (event.pos[0] - SQUARE_SIZE / 2, event.pos[1] - SQUARE_SIZE / 2))
                    pg.display.update()
                if event.type == MOUSEBUTTONUP:
                    is_drag_piece = False
                    if get_square_name(event.pos) in logic.get_legal_squares_for_square(drag_start_square):
                        update_rep(piece, piece_name, get_square_name(event.pos), drag_start_square)
                    blit_board_and_pieces(screen, "", drag_start_square, False)
                    if get_square_name(event.pos) in logic.get_legal_squares_for_square(drag_start_square):
                        screen.blit(piece, (square_to_coords[get_square_name(event.pos)][0], square_to_coords[get_square_name(event.pos)][1]))
                        move = drag_start_square + get_square_name(event.pos)
                        handle_castling(move, screen)
                        handle_en_passant(move)
                        if handle_promotion(move, piece_name, promoted_piece_count):
                            logic.make_move(drag_start_square + get_square_name(event.pos) + 'q')
                            promoted_piece_count += 1
                        else:
                            logic.make_move(drag_start_square + get_square_name(event.pos))
                        white_to_move = False
                    pg.display.update()
    else:
        if not logic.board.is_checkmate:
            print("Draw")
        print("Black won")



# logic
def handle_promotion(move, piece_name, promoted_piece_count):
    # TODO: update int(move[3]) == 8 to support playing as black later
    # TODO: let user input custom promoted piece
    if "P" in piece_name and abs(int(move[1]) - int(move[3])) == 1 and move[3] == "8":
        promoted_piece_name = 'wQ' + str(promoted_piece_count)
        add_to_rep(piece_name_to_piece['wQ40'], promoted_piece_name, move[2:4])
        print(promoted_piece_name)
        return 'q'
    elif "P" in piece_name and abs(int(move[1]) - int(move[3])) == 1 and move[3] == "1":
        promoted_piece_name = 'bQ' + str(promoted_piece_count)
        add_to_rep(piece_name_to_piece['wQ40'], promoted_piece_name, move[2:4])
        return 'q'
    return None


def handle_castling(move, screen):
    number = move[1]
    if move == "e1g1" or move == "e8g8":
        # kingside castle
        if number == "1":
            screen.blit(square_to_piece["h1"], (get_square_coords("f1")))
            update_rep(square_to_piece["h1"], square_to_piece_name["h1"], "f1", "h1")
        else:
            screen.blit(square_to_piece["h8"], (get_square_coords("f8")))
            update_rep(square_to_piece["h8"], square_to_piece_name["h8"], "f8", "h8")
    elif move == "e1c1" or move == "e8c8":
        # queenside castle
        if number == "1":
            screen.blit(square_to_piece["a1"], (get_square_coords("d1")))
            update_rep(square_to_piece["a1"], square_to_piece_name["a1"], "d1", "a1")
        else:
            screen.blit(square_to_piece["a8"], (get_square_coords("c8")))
            update_rep(square_to_piece["a8"], square_to_piece_name["a8"], "d8", "a8")

def handle_en_passant(move):
    if logic.check_en_passant(move):
        target_square = move[2] + move[1]
        delete_from_rep(square_to_piece[target_square], square_to_piece_name[target_square], target_square)

def get_square_name(drag_coords):
    matching_square_coords = (0, 0)
    for i, square_coords in enumerate(get_square_coords_list()):
        if drag_coords[0] >= square_coords[0] and drag_coords[0] <= square_coords[0] + SQUARE_SIZE:
            if drag_coords[1] >= square_coords[1] and drag_coords[1] <= square_coords[1] + SQUARE_SIZE:
                matching_square_coords = square_coords
    return coords_to_square[matching_square_coords]

def update_rep(piece, piece_name, to_square, from_square):
    if to_square in square_to_piece and to_square != from_square:
        # check if piece is already on square, if so, delete from representation
        piece_at_square = square_to_piece[to_square]
        piece_name_at_square = square_to_piece_name[to_square]
        delete_from_rep(piece_at_square, piece_name_at_square, to_square)
    delete_from_rep(piece, piece_name, from_square)
    add_to_rep(piece, piece_name, to_square)

def delete_from_rep(piece, piece_name, square):
    del square_to_piece[square]
    del square_to_piece_name[square]
    del piece_to_square[piece]
    del piece_name_to_square[piece_name]

def add_to_rep(piece, piece_name, square):
    square_to_piece[square] = piece
    square_to_piece_name[square] = piece_name
    piece_to_square[piece] = square
    piece_name_to_square[piece_name] = square

# drawing

def blit_board_and_pieces(screen, excluded_piece_name, square, highlight_squares = True):
    draw_board(screen, highlight_squares, square)
    for square in square_to_piece_name.keys():
        if square_to_piece_name[square] != excluded_piece_name:
            path = square_to_piece_name[square][:2] + ".png"
            draw_piece(path, square_to_coords[square][1], square_to_coords[square][0], square, square_to_piece_name[square], screen)

def draw_board(screen, highlight_squares, square = ""):
    coords = get_square_coords_list()
    is_light = True
    prev_y = 0
    for i, (x, y) in enumerate(coords):
        if i == 0:
            prev_y = y
        if prev_y == y:
            is_light = not is_light
        color = (0, 0, 0)
        if is_light:
            color = colors.LIGHT
        else:
            color = colors.DARK
        if highlight_squares:
            legal_squares = logic.get_legal_squares_for_square(square)
            if coords_to_square[(x, y)] in legal_squares:
                if square_to_color[coords_to_square[(x, y)]]:
                    color = colors.LIGHT_LEGAL_SQUARE
                else:
                    color = colors.DARK_LEGAL_SQUARE
            elif coords_to_square[(x, y)] == square:
                # make start drag square red
                if square_to_color[square]:
                    color = colors.LIGHT_START_SQUARE
                else:
                    color = colors.DARK_START_SQUARE
        draw_square(x, y, color, screen)
        square_to_color[SQUARE_NAMES[i]] = is_light
        square_to_coords[SQUARE_NAMES[i]] = (x, y)
        coords_to_square[(x, y)] = SQUARE_NAMES[i]
        prev_y = y

def draw_square(x1, y1, color, screen):
    pg.draw.rect(screen, color, pg.Rect(x1, y1, x1 + SQUARE_SIZE, y1 + SQUARE_SIZE))

def get_square_coords(square):
    return square_to_coords[square]

def get_square_coords_list():
    coords = []
    for y in range(0, BOARD_SIZE, SQUARE_SIZE):
        for x in range(0, BOARD_SIZE, SQUARE_SIZE):
            coords.append((x, y))
    return coords

def draw_pieces(square_coords, screen):
    colors = ["b", "w"]
    pieces = ["R", "N", "B", "Q", "K", "B", "N", "R"] + ["P"] * 8
    black_piece_coords = square_coords[:16]
    white_piece_coords = square_coords[-8:] + square_coords[-16:-8]
    id = 0
    for color in colors:
        id += 10
        for i, piece in enumerate(pieces):
            id += 1
            path = color + piece + ".png"
            coords = (0, 0)
            if color == "w":
                coords = white_piece_coords[i]
            else:
                coords = black_piece_coords[i]
            piece_name_to_square[color + piece + str(id)] = get_square_name(coords)
            square_to_piece_name[get_square_name(coords)] = color + piece + str(id)
            draw_piece(path, coords[1], coords[0], get_square_name(coords), color + piece + str(id), screen)

def draw_piece(path, x, y, square, piece_name, screen):
    img = pg.image.load(path)
    img.convert()
    square_to_piece[square] = img
    piece_to_square[img] = square
    piece_name_to_piece[piece_name] = img
    screen.blit(img, (y, x))