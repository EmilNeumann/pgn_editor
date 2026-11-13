# coding: utf-8

import functools
import io
import itertools

import chess
import chess.pgn
import chess.svg
import pygame

from . import Widget


BORDER_SIZE = 15
SQUARE_SIZE = 45


# use piece_type and color rather than a chess.Piece instance,
# to make the cache more reliable
@functools.cache
def get_piece_surface(piece_type, color):
    """
    Return a pygame Surface with an SVG of the specified chess piece.
    """
    piece = chess.Piece(piece_type, color)
    piece_svg = chess.svg.piece(piece, size=SQUARE_SIZE)
    buffer = io.BytesIO(piece_svg.encode())
    return pygame.image.load(buffer).convert_alpha()


def get_arrow_color_from_nags(nags: set[int]) -> str:
    """
    Translate numeric annotation glyphs (NAGs)
    to colors for chess.svg.Arrow()
    """
    # Some colors are predefined and are transparent.
    # Specifying transparency when using an RGB code
    # (e.g. "#ff800080") seems to have no effect.
    if not nags: return "green"
    if len(nags) > 1: return "#ff00ff"
    if chess.pgn.NAG_GOOD_MOVE in nags: return "blue"
    if chess.pgn.NAG_MISTAKE in nags: return "#ff8000"
    if chess.pgn.NAG_BRILLIANT_MOVE in nags: return "#00ffff"
    if chess.pgn.NAG_BLUNDER in nags: return "red"
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags: return "#80ff00"
    if chess.pgn.NAG_DUBIOUS_MOVE in nags: return "yellow"
    return "#ff00ff"


class BoardView(Widget):
    """
    A widget that draws a chess board.
    BoardView(parent, [border])

    - parent: The widget / window that directly contains this widget.
              It needs the attributes "selected_node", "show_arrows" and a method "process_move(move)"
    - border: A boolean that indicates whether the board should be drawn with a border.
              See chess.svg.board() for more details
    """
    def __init__(self, parent, border=True):
        super().__init__(parent)
        size = SQUARE_SIZE * 8
        self.border = border
        if border:
            size += BORDER_SIZE * 2
        self.width = self.height = size
        self.active_square = None
        self.orientation = chess.WHITE

    @property
    def selected_node(self):
        return self.parent.selected_node

    def draw(self):
        super().draw()
        board = self.selected_node.game_node.board()
        board_svg = chess.svg.board(
            board,
            orientation=self.orientation,
            arrows=self.get_arrows(),
            fill={self.active_square: "#ff800080"},
            size=self.width,
            borders=self.border
        )
        buffer = io.BytesIO(board_svg.encode())
        board_surface = pygame.image.load(buffer)
        self.surface.blit(board_surface, (0, 0))
        # the board SVG already defines the pieces, but uses references
        # to define their positions. pygame / SDL is apparently unable to
        # handle these references, so this function needs to loop over
        # the board and blit the pieces manually
        for file_index, rank_index in itertools.product(range(8), repeat=2):
            square = chess.square(file_index, rank_index)
            piece = board.piece_at(square)
            if piece is None:
                continue
            piece_surface = get_piece_surface(piece.piece_type, piece.color)
            pos = self.square_to_pixel(file_index, rank_index)
            self.surface.blit(piece_surface, pos)
    
    def click(self, pos):
        file_index, rank_index = self.pixel_to_square(*pos)
        if not (file_index in range(8) and rank_index in range(8)):
            return  # the click was on the border
        square = chess.square(file_index, rank_index)
        if self.active_square is None:
            self.active_square = square
            return
        if self.active_square == square:
            self.active_square = None
            return
        move = chess.Move(self.active_square, square)
        self.active_square = None
        self.parent.process_move(move)

    def get_arrows(self) -> list:
        if not self.parent.show_arrows:
            return []
        if len(self.selected_node.children) <= 1:
            return []
        arrows = []
        for child_node in self.selected_node.children:
            move = child_node.game_node.move
            arrows.append(
                chess.svg.Arrow(
                    move.from_square, move.to_square,
                    color=get_arrow_color_from_nags(child_node.game_node.nags)
                )
            )
        return arrows

    def square_to_pixel(self, file_index, rank_index):
        if self.orientation:
            # from white's perspective the ranks descend from 8 to 1 when
            # comparing against the y axis of the screen coordinate system,
            # so the index numbers need to go from 7 to 0
            rank_index = 7 - rank_index
        else:
            # from black's perspective the files go from H to A
            file_index = 7 - file_index
        x = BORDER_SIZE * self.border + SQUARE_SIZE * file_index
        y = BORDER_SIZE * self.border + SQUARE_SIZE * rank_index
        return x, y

    def pixel_to_square(self, x, y):
        file_index = (x - BORDER_SIZE * self.border) // SQUARE_SIZE
        rank_index = (y - BORDER_SIZE * self.border) // SQUARE_SIZE
        if self.orientation:
            rank_index = 7 - rank_index
        else:
            file_index = 7 - file_index
        return file_index, rank_index
