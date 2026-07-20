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
from treeview import TreeNode


# BORDER = True
BORDER_SIZE = 15
SQUARE_SIZE = 45
BOARD_SIZE = SQUARE_SIZE*8 + BORDER_SIZE*2
CHAR_WIDTH = 10
CHAR_HEIGHT = 21
PLAYER_NAME = "Aemyl"


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
    return pygame.image.load(buffer)


def get_arrow_color_from_nags(nags: set[int]) -> str:
    """
    Translate numeric annotation glyphs (NAGs)
    to colors for chess.svg.Arrow()
    """
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
    """
    Translate numeric annotation glyphs (NAGs)
    to colors for pygame.font.Font.render()
    """
    if not nags: return "#ffffff"
    if len(nags) > 1: return "#ff00ff"
    if chess.pgn.NAG_GOOD_MOVE in nags: return "#00bfff"
    if chess.pgn.NAG_MISTAKE in nags: return "#ff7f00"
    if chess.pgn.NAG_BRILLIANT_MOVE in nags: return "#00bfbf"
    if chess.pgn.NAG_BLUNDER in nags: return "#ff3f00"
    if chess.pgn.NAG_SPECULATIVE_MOVE in nags: return "#7fff00"
    if chess.pgn.NAG_DUBIOUS_MOVE in nags: return "#ffdf00"
    return "#ff00ff"


def get_lines(tree_node, indentation):
    """
    Group tree nodes into lines:
    - if a node has no child nodes, the line ends
    - if a node has only one child node, they should be on the same line
    - if a node has multiple child nodes, each child node starts a new
      line with increased indentation
    """
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


class EventHandler:
    """
    Abstract base class.
    Subclasses control how the user can interact with the program.
    """
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
    """
    This mode turns the window into a file dialog.
    """
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
            if self.selected_index is None:
                return
            if self.selection == Selection.FILES:
                pass  # TODO: determine selected file, update_list()
            elif self.selection == Selection.GAMES:
                pass  # TODO: open selected game and switch to ReplayMode
    
    def mouse_button_down(self, event):
        pass  # TODO: convert y position to list index
    
    def update_list(self):
        self.items.clear()
        if self.selection == Selection.FILES:
            for filename in os.listdir(self.directory):
                if filename.endswith('.pgn'):
                    self.items.append(filename)
        if self.selection == Selection.GAMES:
            pass  # TODO: get games from selected file and include a summary in the list


class BoardEventHandler(EventHandler):
    """
    Base class for event handlers that allow interaction with a chess board.
    """
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
    """
    This mode allows the user to explore the entire game tree.
    """
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
    """
    This mode is intended for practicing.
    
    The treeview is replaced by a move list that leads to the current
    position, arrows are not shown in positions with multiple variations
    and comments are only shown when the end of a line is reached.
    
    When this mode is entered, it remembers the current position, so the
    user can jump back to it by pressing <R>.
    """
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
            # reset to start node
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
        self.surface = pygame.display.set_mode(
            (BOARD_SIZE+700, BOARD_SIZE+500),
            flags=pygame.RESIZABLE
            # flags=pygame.FULLSCREEN
        )
        pygame.display.set_caption("PGN Editor")
        self.font = pygame.font.SysFont('sourcecodepro', 16)
        self.orientation = chess.WHITE
        with open('pgn/jaenisch_gambit.pgn') as f:
            root = chess.pgn.read_game(f)
            if root.headers["Black"] == PLAYER_NAME:
                self.orientation = chess.BLACK
        self.root = TreeNode(root, None)
        # self.positions = {}
        # transpositions.get_positions(self.root.game_node, self.positions)
        self.mode = ReplayMode(self)
        self.visible_nodes = []
        self.selected_node = self.root
        self.treeview_pos = (BOARD_SIZE + BORDER_SIZE, 0)
        self.update_treeview()
    
    def mainloop(self):
        clock = pygame.time.Clock()
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
            clock.tick(60)
    
    def update_treeview(self):
        """
        Determine which nodes are visible and where they are.
        """
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
                    tree_node.text += f" ({len(tree_node.children)}"
                    tree_node.text += f"/{tree_node.get_subtree_lines()}/"
                    tree_node.text += f"{tree_node.get_subtree_size()})"
                tree_node.width = len(tree_node.text) * CHAR_WIDTH
                tree_node.height = CHAR_HEIGHT
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
        pass  # TODO: iterate over self.mode.items and print each in a new line, highlighting the selected item
    
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
    pygame.init()
    Window().mainloop()
    pygame.quit()


if __name__ == '__main__':
    main()
