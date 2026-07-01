# coding: utf-8


from enum import Enum, auto
import functools
import io
import itertools
import os.path
import random

import chess
import chess.pgn
import chess.svg
import pygame

import transpositions

OPENING_PGN='pgn/scotch_game.pgn'

# BORDER = True
PIECE_SIZE = 65
BORDER_SIZE = 25
SQUARE_SIZE = 65
BOARD_SIZE = SQUARE_SIZE*8 + BORDER_SIZE*2

CHAR_WIDTH = 15
CHAR_HEIGHT = 23

FONT_SIZE = 15
FONT_TYPE = 'arial'

# TODO: introduce true randomness (even distribution) for random moves
# not possible with random.seed(42)
# TODO K_RETURN: 
# TODO MOUSE_DOWN:


PLAYER_NAME = "Aemyl"



@functools.cache
def get_piece_surface(piece_type, color):
    piece = chess.Piece(piece_type, color)
    piece_svg = chess.svg.piece(piece, size=PIECE_SIZE)
    buffer = io.BytesIO(piece_svg.encode())
    return pygame.image.load(buffer)


def get_arrow_color_from_nags(nags: set[int]) -> str:
    if not nags: return "green"
    if len(nags) > 1: return "#ff00ff"
    if chess.pgn.NAG_GOOD_MOVE in nags: return "blue"
    if chess.pgn.NAG_MISTAKE in nags: return "#ff8000"
    if chess.pgn.NAG_BRILLIANT_MOVE in nags: return "#00ffff"
    if chess.pgn.NAG_BLUNDER in nags: return "red"
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags: return "#80ff00"
    if chess.pgn.NAG_DUBIOUS_MOVE in nags: return "yellow"
    return "#ff00ff"


def get_text_color_from_nags(nags: set[int]) -> str:
    if not nags: return "#ffffff"
    if len(nags) > 1: return "#ff00ff"
    if chess.pgn.NAG_GOOD_MOVE in nags: return "#00bfff"
    if chess.pgn.NAG_MISTAKE in nags: return "#ff7f00"
    if chess.pgn.NAG_BRILLIANT_MOVE in nags: return "#00bfbf"
    if chess.pgn.NAG_BLUNDER in nags: return "#ff3f00"
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags: return "#7fff00"
    if chess.pgn.NAG_DUBIOUS_MOVE in nags: return "#ffdf00"
    return "#ff00ff"


def get_text_from_nags(nags: set[int]) -> str:
    if not nags: return ""
    if len(nags) > 1: return "[?]"
    if chess.pgn.NAG_GOOD_MOVE in nags: return "!"
    if chess.pgn.NAG_MISTAKE in nags: return "?"
    if chess.pgn.NAG_BRILLIANT_MOVE in nags: return "!!"
    if chess.pgn.NAG_BLUNDER in nags: return "??"
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags: return "!?"
    if chess.pgn.NAG_DUBIOUS_MOVE in nags: return "?!"
    return "[?]"


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
        self.base_text = ""
        self.fen = transpositions.shorten_fen(game_node.board().fen())
        if game_node.parent is not None:
            board = game_node.parent.board()
            if board.turn == chess.WHITE:
                self.base_text += f"{board.fullmove_number}. "
            elif len(parent.game_node.variations) > 1:
                self.base_text += f"{board.fullmove_number}... "
            self.base_text += board.san(game_node.move)
            self.base_text += get_text_from_nags(game_node.nags)
        self.children = [
            TreeNode(child, self)
            for child in game_node.variations
        ]
        # the following attributes are managed by the Window class
        self.text = self.base_text
        self.position = (0, 0)
        self.width = CHAR_WIDTH * len(self.text)
        self.height = CHAR_HEIGHT
    
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
        return len(self.children) + sum(
            child.get_subtree_size() for child in self.children
        )


class EventHandler:
    def __init__(self, parent):
        self.parent: Window = parent
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
            self.selected_index = min(
                len(self.items) - 1,
                (self.selected_index or 0) + 1
            )
        if event.key == pygame.K_RETURN:
            pass  # TODO Event Return
    
    def mouse_button_down(self, event):
        pass  # TODO Event Mouse Down
    
    def update_list(self):
        self.items.clear()
        if self.selection == Selection.FILES:
            pass  # TODO Event3
        if self.selection == Selection.GAMES:
            pass  # TODO Event4


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
        pass


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
            # reset to root node
            self.parent.selected_node = self.start_node
            if self.start_node.game_node.turn() != self.color:
                self.parent.make_random_move()
        if event.key == pygame.K_x:
            self.parent.exit_practice_mode()
    
    def process_move(self, move):
        correct = False
        children = self.parent.selected_node.children
        if not children:
            print("variation ended")
            return
        if not self.parent.selected_node.game_node.board().is_legal(move):
            return
        for child_node in children:
            if child_node.game_node.move == move:
                correct = True
                self.parent.selected_node = child_node
                break
        if correct:
            print("correct")
            self.parent.make_random_move()
        else:
            print("wrong")
    
    def get_info(self) -> str:
        variation_count = len(self.parent.selected_node.children)
        if variation_count:
            return f"{variation_count} variations"
        return self.parent.selected_node.game_node.comment


class Window:
    def __init__(self):
        self.orientation = chess.WHITE
        with open(OPENING_PGN) as f:
            self.root = chess.pgn.read_game(f)
            if self.root.headers["Black"] == PLAYER_NAME:
                self.orientation = chess.BLACK
        self.root = TreeNode(self.root, None)
        self.positions = {}
        transpositions.get_positions(self.root.game_node, self.positions)
        self.mode = ReplayMode(self)
        self.surface = None
        self.font = None
        self.visible_nodes = []
        self.selected_node = self.root
        self.treeview_pos = (BOARD_SIZE + BORDER_SIZE, 0)
        self.tree_text = []
        # self.init_treeview()
    
    def mainloop(self):
        pygame.init()
        self.surface = pygame.display.set_mode(
            (BOARD_SIZE+700, BOARD_SIZE+500),
            flags=pygame.RESIZABLE
            # flags=pygame.FULLSCREEN
        )
        self.font = pygame.font.SysFont(FONT_TYPE, FONT_SIZE)
        self.update_treeview()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    self.mode.key_down(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mode.mouse_button_down(event)
            self.draw()
            pygame.display.flip()
        pygame.quit()
    
    def init_treeview(self):
        self.tree_text = []
        lines = []  # list of tuples (indentation, moves)
        current_line = []  # list of tuples (board, move)
        start_node = self.node
        if start_node.parent is None:
            start_node = start_node.variation(0)
        unprocessed_nodes = [(0, start_node)]
        while unprocessed_nodes:
            indentation, node = unprocessed_nodes.pop()
            current_line.append((node.parent.board(), node.move))
            match len(node.variations):
                case 0:
                    lines.append((indentation, current_line))
                    current_line = []
                    indentation -= 1
                case 1:
                    unprocessed_nodes.append((indentation, node.variation(0)))
                case _:
                    lines.append((indentation, current_line))
                    current_line = []
                    indentation += 1
                    for child_node in reversed(node.variations):
                        unprocessed_nodes.append((indentation, child_node))
        for indentation, line in lines:
            text = "  " * indentation
            board = line[0][0]
            if board.turn == chess.BLACK:
                text += f"{board.fullmove_number}... "
            for board, move in line:
                if board.turn == chess.WHITE:
                    text += f"{board.fullmove_number}. "
                text += board.san(move) + ' '
            self.tree_text.append(text.rstrip())
    
    def update_treeview(self):
        self.visible_nodes.clear()
        self.selected_node.make_visible()
        lines = get_lines(self.root, 0)
        offset_x, offset_y = self.treeview_pos
        for line_index, line in enumerate(lines):
            indentation, tree_nodes = line
            y = offset_y + line_index * CHAR_HEIGHT
            x = offset_x + indentation * 2 * CHAR_WIDTH
            for tree_node in tree_nodes:
                tree_node.position = (x, y)
                tree_node.text = tree_node.base_text
                if not tree_node.expanded and len(tree_node.children) > 1:
                    tree_node.text += f" ({tree_node.get_subtree_size()})"
                tree_node.width = len(tree_node.text) * CHAR_WIDTH
                self.visible_nodes.append(tree_node)
                x += tree_node.width + CHAR_WIDTH
    
    def draw(self):
        self.surface.fill("#000000")  # clear
        if self.mode.show_list:
            self.draw_list()
        if self.mode.show_board:
            self.draw_board()
            if self.mode.show_tree:
                self.draw_tree_view()
            if self.mode.show_move_list:
                self.draw_move_list()
            self.draw_info()
    
    def draw_list(self):
        pass
    
    def draw_board(self):
        board = self.selected_node.game_node.board()
        board_svg = chess.svg.board(
            board,
            orientation=self.orientation,
            arrows=self.get_arrows(),
            fill={self.mode.active_square: "#ff800080"},
            size=BOARD_SIZE
        )
        buffer = io.BytesIO(board_svg.encode())
        board_surface = pygame.image.load(buffer)
        self.surface.blit(board_surface, (0, 0))
        for file_index, rank_index in itertools.product(range(8), repeat=2):
            square = chess.square(file_index, rank_index)
            piece = board.piece_at(square)
            if piece is None:
                continue
            piece_surface = get_piece_surface(piece.piece_type, piece.color)
            pos = self.square_to_pixel(file_index, rank_index)
            self.surface.blit(piece_surface, pos)
    
    def draw_move_list(self):
        pgn = str(chess.pgn.Game.from_board(self.selected_node.game_node.board()))
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
            text_surface = self.font.render(
                ' '.join(line),
                False,
                "#ffffff",
                "#000000"
            )
            self.surface.blit(text_surface, (BOARD_SIZE + BORDER_SIZE, total_height))
            total_height += text_surface.get_height()
    
    def draw_info(self):
        text = self.mode.get_info().encode('latin-1')
        max_line_length = BOARD_SIZE // CHAR_WIDTH
        for i, line in enumerate(itertools.batched(text, max_line_length)):
            comment_surface = self.font.render(
                bytes(line),
                False,
                "#ffffff",
                "#000000"
            )
            self.surface.blit(comment_surface, (0, BOARD_SIZE + BORDER_SIZE + CHAR_HEIGHT * i))
    
    def draw_tree_view(self):
        # total_height = 0
        # for text in self.tree_text:
        #     text_surface = self.font.render(
        #         text, False, "#ffffff", "#000000"
        #     )
        #     self.surface.blit(text_surface, (BOARD_SIZE + BORDER_SIZE, total_height))
        #     total_height += text_surface.get_height()
        for node in self.visible_nodes:
            background = "#000000"
            if node is self.selected_node:
                background = "#0000ff"
            elif node.fen == self.selected_node.fen:
                background = "#00007f"
            elif node.game_node.comment:
                background = "#3f3f3f"
            text_surface = self.font.render(
                node.text,
                False,
                get_text_color_from_nags(node.game_node.nags),
                background
            )
            self.surface.blit(text_surface, node.position)
    
    def get_arrows(self) -> list:
        if not self.mode.show_arrows:
            return []
        if len(self.selected_node.children) <= 1:
            return []
        arrows = []
        for child_node in self.selected_node.children:
            arrows.append(
                chess.svg.Arrow(
                    child_node.game_node.move.from_square,
                    child_node.game_node.move.to_square,
                    color=get_arrow_color_from_nags(child_node.game_node.nags)
                )
            )
        return arrows
    
    def flip_board(self):
        self.orientation = not self.orientation
    
    def make_random_move(self):
        if self.selected_node.children:
            self.selected_node = random.choice(self.selected_node.children)
    
    def square_to_pixel(self, file_index, rank_index):
        if self.orientation:
            rank_index = 7 - rank_index
        else:
            file_index = 7 - file_index
        x = BORDER_SIZE + SQUARE_SIZE*file_index
        y = BORDER_SIZE + SQUARE_SIZE*rank_index
        return x, y
    
    def pixel_to_square(self, x, y):
        file_index = (x - BORDER_SIZE) // SQUARE_SIZE
        rank_index = (y - BORDER_SIZE) // SQUARE_SIZE
        if self.orientation:
            rank_index = 7 - rank_index
        else:
            file_index = 7 - file_index
        return file_index, rank_index
    
    def enter_practice_mode(self):
        self.mode = PracticeMode(self, self.orientation)
    
    def exit_practice_mode(self):
        self.mode = ReplayMode(self)
        self.update_treeview()


def main():
    Window().mainloop()


if __name__ == '__main__':
    main()
