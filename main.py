# coding: utf-8


import functools
import io
import itertools

import chess
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
    
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bb5")
    board.push_san("f5")
    
    orientation = chess.BLACK
    
    draw_board(board, orientation)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # print(event)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
