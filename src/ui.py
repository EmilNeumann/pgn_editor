# coding: utf-8

import functools
import io
import os.path
import random
from enum import Enum, auto

import chess
import chess.pgn
import chess.svg
import pygame

from src import config
from src import transpositions


@functools.cache
def get_piece_surface(piece_type, color):
    piece = chess.Piece(piece_type, color)
    piece_svg = chess.svg.piece(piece, size=config.PIECE_SIZE)
    buffer = io.BytesIO(piece_svg.encode())
    return pygame.image.load(buffer)


def get_arrow_color_from_nags(nags: set[int]) -> str:
    if not nags:
        return 'green'
    if len(nags) > 1:
        return '#ff00ff'
    if chess.pgn.NAG_GOOD_MOVE in nags:
        return 'blue'
    if chess.pgn.NAG_MISTAKE in nags:
        return '#ff8000'
    if chess.pgn.NAG_BRILLIANT_MOVE in nags:
        return '#00ffff'
    if chess.pgn.NAG_BLUNDER in nags:
        return 'red'
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags:
        return '#80ff00'
    if chess.pgn.NAG_DUBIOUS_MOVE in nags:
        return 'yellow'
    return '#ff00ff'


def get_text_color_from_nags(nags: set[int]) -> str:
    if not nags:
        return '#ffffff'
    if len(nags) > 1:
        return '#ff00ff'
    if chess.pgn.NAG_GOOD_MOVE in nags:
        return '#00bfff'
    if chess.pgn.NAG_MISTAKE in nags:
        return '#ff7f00'
    if chess.pgn.NAG_BRILLIANT_MOVE in nags:
        return '#00bfbf'
    if chess.pgn.NAG_BLUNDER in nags:
        return '#ff3f00'
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags:
        return '#7fff00'
    if chess.pgn.NAG_DUBIOUS_MOVE in nags:
        return '#ffdf00'
    return '#ff00ff'


def get_text_from_nags(nags: set[int]) -> str:
    if not nags:
        return ''
    if len(nags) > 1:
        return '[?]'
    if chess.pgn.NAG_GOOD_MOVE in nags:
        return '!'
    if chess.pgn.NAG_MISTAKE in nags:
        return '?'
    if chess.pgn.NAG_BRILLIANT_MOVE in nags:
        return '!!'
    if chess.pgn.NAG_BLUNDER in nags:
        return '??'
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags:
        return '!?'
    if chess.pgn.NAG_DUBIOUS_MOVE in nags:
        return '?!'
    return '[?]'


def get_lines(tree_node, indentation):
    lines = []
    line = []
    while len(tree_node.children) == 1:
        line.append(tree_node)
        tree_node = tree_node.children[0]
    line.append(tree_node)
    lines.append((indentation, line))
    if tree_node.expanded:
        for child in tree_node.children:
            lines.extend(get_lines(child, indentation + 1))
    return lines


class TreeNode:
    def __init__(self, game_node, parent):
        self.game_node = game_node
        self.parent = parent
        self.expanded = False
        self.base_text = ''
        self.fen = transpositions.shorten_fen(game_node.board().fen())
        if game_node.parent is not None:
            board = game_node.parent.board()
            if board.turn == chess.WHITE:
                self.base_text += f'{board.fullmove_number}. '
            elif len(parent.game_node.variations) > 1:
                self.base_text += f'{board.fullmove_number}... '
            self.base_text += board.san(game_node.move)
            self.base_text += get_text_from_nags(game_node.nags)
        self.children = [TreeNode(child, self) for child in game_node.variations]
        self.text = self.base_text
        self.position = (0, 0)
        self.width = config.CHAR_WIDTH * len(self.text)
        self.height = config.CHAR_HEIGHT

    def expand(self):
        self.expanded = True

    def collapse(self):
        self.expanded = False

    def expand_all(self):
        self.expand()
        for child in self.children:
            child.expand_all()

    def collapse_all(self):
        for child in self.children:
            child.collapse_all()
        self.collapse()

    def toggle(self):
        if self.expanded:
            self.collapse()
        else:
            self.expand()

    def make_visible(self):
        if self.parent is None:
            return
        self.parent.expand()
        self.parent.make_visible()

    def get_subtree_size(self):
        return len(self.children) + sum(child.get_subtree_size() for child in self.children)


class EventHandler:
    def __init__(self, parent):
        self.parent = parent
        self.show_list = False
        self.show_board = False

    def key_down(self, event):
        pass

    def mouse_button_down(self, event):
        pass


class Selection(Enum):
    FILES = auto()
    GAMES = auto()


class FileSelectorMode(EventHandler):
    def __init__(self, parent):
        super().__init__(parent)
        self.show_list = True
        self.selection = Selection.FILES
        self.selected_index = None
        self.directory = os.path.abspath('pgn')
        self.items = []

    def key_down(self, event):
        if event.key == pygame.K_UP:
            self.selected_index = max(0, (self.selected_index or 0) - 1)
        if event.key == pygame.K_DOWN:
            self.selected_index = min(len(self.items) - 1, (self.selected_index or 0) + 1)
        if event.key == pygame.K_RETURN:
            pass

    def mouse_button_down(self, event):
        pass

    def update_list(self):
        self.items.clear()
        if self.selection == Selection.FILES:
            pass
        if self.selection == Selection.GAMES:
            pass


class BoardEventHandler(EventHandler):
    def __init__(self, parent):
        super().__init__(parent)
        self.active_square = None
        self.show_board = True
        self.show_arrows = True
        self.show_tree = False
        self.show_move_list = False

    def mouse_button_down(self, event):
        x, y = event.pos
        file_index, rank_index = self.parent.pixel_to_square(x, y)
        if file_index in range(8) and rank_index in range(8):
            square = chess.square(file_index, rank_index)
            if self.active_square is None:
                self.active_square = square
                return
            if self.active_square == square:
                self.active_square = None
                return
            move = chess.Move(self.active_square, square)
            self.active_square = None
            self.process_move(move)
        elif self.show_tree:
            for node in self.parent.visible_nodes:
                node_x, node_y = node.position
                if x in range(node_x, node_x + node.width) and y in range(node_y, node_y + node.height):
                    self.parent.selected_node = node
                    break
            self.parent.update_treeview()
        self.active_square = None

    def process_move(self, move):
        pass

    def get_info(self) -> str:
        return ''


class ReplayMode(BoardEventHandler):
    def __init__(self, parent):
        super().__init__(parent)
        self.show_tree = True

    def key_down(self, event):
        if event.key == pygame.K_f:
            self.parent.flip_board()
        if event.key == pygame.K_x:
            self.parent.enter_practice_mode()
        node = self.parent.selected_node
        if event.key == pygame.K_LEFT:
            self.parent.selected_node = node.parent or node
        if event.key == pygame.K_RIGHT:
            self.parent.make_random_move()
        if event.key == pygame.K_SPACE:
            node.toggle()
        if event.key == pygame.K_PLUS:
            node.expand_all()
        if event.key == pygame.K_MINUS:
            node.collapse_all()
        self.parent.update_treeview()

    def process_move(self, move):
        for child_node in self.parent.selected_node.children:
            if child_node.game_node.move == move:
                self.parent.selected_node = child_node
                self.parent.update_treeview()
                break

    def get_info(self) -> str:
        return self.parent.selected_node.game_node.comment


class PracticeMode(BoardEventHandler):
    def __init__(self, parent, color):
        super().__init__(parent)
        self.show_arrows = False
        self.show_move_list = True
        self.color = color
        self.start_node = self.parent.selected_node
        if self.start_node.game_node.turn() != color:
            self.parent.make_random_move()

    def key_down(self, event):
        if event.key == pygame.K_f:
            self.parent.flip_board()
        if event.key == pygame.K_r:
            self.parent.selected_node = self.start_node
            if self.start_node.game_node.turn() != self.color:
                self.parent.make_random_move()
        if event.key == pygame.K_x:
            self.parent.exit_practice_mode()

    def process_move(self, move):
        correct = False
        children = self.parent.selected_node.children
        if not children:
            print('variation ended')
            return
        if not self.parent.selected_node.game_node.board().is_legal(move):
            return
        for child_node in children:
            if child_node.game_node.move == move:
                correct = True
                self.parent.selected_node = child_node
                break
        if correct:
            print('correct')
            self.parent.make_random_move()
        else:
            print('wrong')

    def get_info(self) -> str:
        variation_count = len(self.parent.selected_node.children)
        if variation_count:
            return f'{variation_count} variations'
        return self.parent.selected_node.game_node.comment
