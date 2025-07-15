# coding: utf-8


import functools
import io
import itertools
import random

import chess
import chess.pgn
import chess.svg
import pygame


SIZE = 390


@functools.cache
def get_piece_surface(piece_type, color):
    piece = chess.Piece(piece_type, color)
    piece_svg = chess.svg.piece(piece, size=45)
    buffer = io.BytesIO(piece_svg.encode())
    return pygame.image.load(buffer)


def get_coordinates(file_index, rank_index, orientation, border):
    if orientation:
        rank_index = 7 - rank_index
    else:
        file_index = 7 - file_index
    x = 15*border + 45*file_index
    y = 15*border + 45*rank_index
    return x, y


def draw_board(board, orientation):
    window = pygame.display.get_surface()
    board_svg = chess.svg.board(board, orientation=orientation, size=SIZE)
    buffer = io.BytesIO(board_svg.encode())
    board_surface = pygame.image.load(buffer)
    window.blit(board_surface, (0, 0))
    for file_index, rank_index in itertools.product(range(8), repeat=2):
        square = chess.square(file_index, rank_index)
        piece = board.piece_at(square)
        if piece is None:
            continue
        piece_surface = get_piece_surface(piece.piece_type, piece.color)
        x, y = get_coordinates(file_index, rank_index, orientation, True)
        window.blit(piece_surface, (x, y))


def main():
    pygame.init()
    window = pygame.display.set_mode((SIZE, SIZE))
    
    with open('test.pgn') as f:
        game = chess.pgn.read_game(f)
    
    board = game.board()
    node = game
    
    orientation = chess.BLACK
    
    draw_board(board, orientation)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    orientation = not orientation
                    draw_board(board, orientation)
                if event.key == pygame.K_LEFT:
                    node = node.parent or node
                    board = node.board()
                    draw_board(board, orientation)
                if event.key == pygame.K_RIGHT:
                    if node.variations:
                        node = random.choice(node.variations)
                    board = node.board()
                    draw_board(board, orientation)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
