# coding: utf-8

import io
import itertools
import random

import chess
import chess.pgn
import chess.svg
import pygame

from src import config
from src import transpositions


class GameView:
    def __init__(self, window):
        self.window = window
        self.surface = None
        self.font = None

    @property
    def surface_view(self):
        if self.surface is None:
            self.surface = self.window.surface
        return self.surface

    @property
    def font_view(self):
        if self.font is None:
            self.font = self.window.font
        return self.font

    def draw(self):
        surface = self.surface_view
        if surface is None:
            return
        surface.fill('#000000')
        if self.window.mode.show_list:
            self.draw_list()
        if self.window.mode.show_board:
            self.draw_board()
            if self.window.mode.show_tree:
                self.draw_tree_view()
            if self.window.mode.show_move_list:
                self.draw_move_list()
            self.draw_info()

    def draw_list(self):
        pass

    def draw_board(self):
        board = self.window.selected_node.game_node.board()
        board_svg = chess.svg.board(
            board,
            orientation=self.window.orientation,
            arrows=self.get_arrows(),
            fill={self.window.mode.active_square: '#ff800080'},
            size=config.BOARD_SIZE,
        )
        buffer = io.BytesIO(board_svg.encode())
        board_surface = pygame.image.load(buffer)
        self.surface_view.blit(board_surface, (0, 0))
        for file_index, rank_index in itertools.product(range(8), repeat=2):
            square = chess.square(file_index, rank_index)
            piece = board.piece_at(square)
            if piece is None:
                continue
            piece_surface = self._get_piece_surface(piece.piece_type, piece.color)
            pos = self.window.square_to_pixel(file_index, rank_index)
            self.surface_view.blit(piece_surface, pos)

    def draw_move_list(self):
        pgn = str(chess.pgn.Game.from_board(self.window.selected_node.game_node.board()))
        moves = pgn.rpartition('\n')[-1]
        parts = moves.split(' ')
        lines = []
        line = []
        for part in parts:
            if part.endswith('.'):
                if line:
                    lines.append(line)
                line = []
            line.append(part)
        if line:
            lines.append(line)
        total_height = 0
        for line in lines:
            text_surface = self.font_view.render(
                ' '.join(line),
                False,
                '#ffffff',
                '#000000',
            )
            self.surface_view.blit(text_surface, (config.BOARD_SIZE + config.BORDER_SIZE, total_height))
            total_height += text_surface.get_height()

    def draw_info(self):
        text = self.window.mode.get_info().encode('latin-1')
        max_line_length = config.BOARD_SIZE // config.CHAR_WIDTH
        for i, line in enumerate(itertools.batched(text, max_line_length)):
            comment_surface = self.font_view.render(
                bytes(line),
                False,
                '#ffffff',
                '#000000',
            )
            self.surface_view.blit(comment_surface, (0, config.BOARD_SIZE + config.BORDER_SIZE + config.CHAR_HEIGHT * i))

    def draw_tree_view(self):
        for node in self.window.visible_nodes:
            background = '#000000'
            if node is self.window.selected_node:
                background = '#0000ff'
            elif node.fen == self.window.selected_node.fen:
                background = '#00007f'
            elif node.game_node.comment:
                background = '#3f3f3f'
            text_surface = self.font_view.render(
                node.text,
                False,
                self.window.get_text_color_from_nags(node.game_node.nags),
                background,
            )
            self.surface_view.blit(text_surface, node.position)

    def get_arrows(self):
        if not self.window.mode.show_arrows:
            return []
        if len(self.window.selected_node.children) <= 1:
            return []
        arrows = []
        for child_node in self.window.selected_node.children:
            arrows.append(
                chess.svg.Arrow(
                    child_node.game_node.move.from_square,
                    child_node.game_node.move.to_square,
                    color=self.window.get_arrow_color_from_nags(child_node.game_node.nags),
                )
            )
        return arrows

    @staticmethod
    def _get_piece_surface(piece_type, color):
        piece = chess.Piece(piece_type, color)
        piece_svg = chess.svg.piece(piece, size=config.PIECE_SIZE)
        buffer = io.BytesIO(piece_svg.encode())
        return pygame.image.load(buffer)
