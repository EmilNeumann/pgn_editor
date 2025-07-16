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


def get_color_from_nags(nags: set[int]) -> str:
    if not nags:
        return "green"
    if len(nags) > 1:
        return "#ff00ff"
    if chess.pgn.NAG_GOOD_MOVE in nags:
        return "blue"
    if chess.pgn.NAG_MISTAKE in nags:
        return "#ff8000"
    if chess.pgn.NAG_BRILLIANT_MOVE in nags:
        return "#00ffff"
    if chess.pgn.NAG_BLUNDER in nags:
        return "red"
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags:
        return "#80ff00"
    if chess.pgn.NAG_DUBIOUS_MOVE in nags:
        return "yellow"
    return "#ff00ff"


def draw(node, orientation):
    window = pygame.display.get_surface()
    board = node.board()
    arrows = []
    if len(node.variations) > 1:
        for child_node in node.variations:
            arrows.append(
                chess.svg.Arrow(
                    child_node.move.from_square,
                    child_node.move.to_square,
                    color=get_color_from_nags(child_node.nags)
                )
            )
    board_svg = chess.svg.board(
        board,
        orientation=orientation,
        arrows=arrows,
        size=SIZE
    )
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
    
    node = game
    
    orientation = chess.BLACK
    
    draw(node, orientation)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    orientation = not orientation
                    draw(node, orientation)
                if event.key == pygame.K_LEFT:
                    node = node.parent or node
                    draw(node, orientation)
                if event.key == pygame.K_RIGHT:
                    if node.variations:
                        node = random.choice(node.variations)
                        draw(node, orientation)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
