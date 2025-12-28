# coding: utf-8


import functools
import io
import itertools
import random

import chess
import chess.pgn
import chess.svg
import pygame

import transpositions


# BORDER = True
BORDER_SIZE = 15
SQUARE_SIZE = 45
SIZE = SQUARE_SIZE*8 + BORDER_SIZE*2
PLAYER_NAME = "Aemyl"


@functools.cache
def get_piece_surface(piece_type, color):
    piece = chess.Piece(piece_type, color)
    piece_svg = chess.svg.piece(piece, size=45)
    buffer = io.BytesIO(piece_svg.encode())
    return pygame.image.load(buffer)


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


class EventHandler:
    def __init__(self, parent):
        self.parent: Window = parent
        self.active_square = None
        self.show_arrows = True
        self.show_tree = True
    
    def key_down(self, event):
        pass
    
    def mouse_button_down(self, event):
        x, y = event.pos
        file_index, rank_index = self.parent.pixel_to_square(x, y)
        if file_index not in range(8) or rank_index not in range(8):
            return
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
    
    def process_move(self, move):
        pass
    
    def get_info(self) -> str:
        pass


class ReplayMode(EventHandler):
    def key_down(self, event):
        if event.key == pygame.K_f:
            self.parent.flip_board()
        if event.key == pygame.K_x:
            self.parent.enter_practice_mode()
        node = self.parent.node
        if event.key == pygame.K_LEFT:
            self.parent.node = node.parent or node
        if event.key == pygame.K_RIGHT:
            self.parent.make_random_move()
    
    def process_move(self, move):
        for child_node in self.parent.node.variations:
            if child_node.move == move:
                self.parent.node = child_node
                break
    
    def get_info(self) -> str:
        return self.parent.node.comment


class PracticeMode(EventHandler):
    def __init__(self, parent, color):
        super().__init__(parent)
        self.show_arrows = False
        self.show_tree = False
        self.color = color
        self.start_node = self.parent.node
        if self.start_node.turn() != color:
            self.parent.make_random_move()
    
    def key_down(self, event):
        if event.key == pygame.K_f:
            self.parent.flip_board()
        if event.key == pygame.K_r:
            # reset to root node
            self.parent.node = self.start_node
            if self.start_node.turn() != self.color:
                self.parent.make_random_move()
        if event.key == pygame.K_x:
            self.parent.exit_practice_mode()
    
    def process_move(self, move):
        correct = False
        variations = self.parent.node.variations
        if not variations:
            print("variation ended")
            return
        if not self.parent.node.board().is_legal(move):
            return
        for child_node in variations:
            if child_node.move == move:
                correct = True
                self.parent.node = child_node
                break
        if correct:
            print("correct")
            self.parent.make_random_move()
        else:
            print("wrong")
    
    def get_info(self) -> str:
        variation_count = len(self.parent.node.variations)
        if variation_count:
            return f"{variation_count} variations"
        return self.parent.node.comment


class Window:
    def __init__(self):
        self.orientation = chess.WHITE
        with open('pgn/owen_defense.pgn') as f:
            game = chess.pgn.read_game(f)
            if game.headers["Black"] == PLAYER_NAME:
                self.orientation = chess.BLACK
        self.node = game
        self.positions = {}
        transpositions.get_positions(game, self.positions)
        self.mode = ReplayMode(self)
        self.surface = None
        self.font = None
        self.tree_text = []
        self.init_treeview()
    
    def mainloop(self):
        pygame.init()
        self.surface = pygame.display.set_mode((SIZE+700, SIZE+500))
        self.font = pygame.font.SysFont('sourcecodepro', 16)
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
        lines = []  # list of tuples (indentation, moves)
        current_line = []  # list of tuples (board, move)
        unprocessed_nodes = [(0, self.node.game().variation(0))]
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
    
    def draw(self):
        self.surface.fill("#000000")  # clear
        self.draw_board()
        if self.mode.show_tree:
            self.draw_tree_view()
        else:
            self.draw_move_list()
        self.draw_info()
    
    def draw_board(self):
        board = self.node.board()
        board_svg = chess.svg.board(
            board,
            orientation=self.orientation,
            arrows=self.get_arrows(),
            fill={self.mode.active_square: "#ff800080"},
            size=SIZE
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
        pgn = str(chess.pgn.Game.from_board(self.node.board()))
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
            self.surface.blit(text_surface, (SIZE+BORDER_SIZE, total_height))
            total_height += text_surface.get_height()
    
    def draw_info(self):
        comment_surface = self.font.render(
            self.mode.get_info().encode('latin-1'),
            False,
            "#ffffff",
            "#000000"
        )
        self.surface.blit(comment_surface, (0, SIZE + BORDER_SIZE))
    
    def draw_tree_view(self):
        total_height = 0
        for text in self.tree_text:
            text_surface = self.font.render(
                text, False, "#ffffff", "#000000"
            )
            self.surface.blit(text_surface, (SIZE+BORDER_SIZE, total_height))
            total_height += text_surface.get_height()
    
    def get_arrows(self) -> list:
        if not self.mode.show_arrows:
            return []
        if len(self.node.variations) <= 1:
            return []
        arrows = []
        for child_node in self.node.variations:
            arrows.append(
                chess.svg.Arrow(
                    child_node.move.from_square,
                    child_node.move.to_square,
                    color=get_color_from_nags(child_node.nags)
                )
            )
        return arrows
    
    def flip_board(self):
        self.orientation = not self.orientation
    
    def make_random_move(self):
        if self.node.variations:
            self.node = random.choice(self.node.variations)
    
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


def main():
    Window().mainloop()


if __name__ == '__main__':
    main()
