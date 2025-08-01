# coding: utf-8


import functools
import io
import itertools
import random

import chess
import chess.pgn
import chess.svg
import pygame


BORDER = True
SIZE = 45*8 + 30*BORDER


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
    
    def key_down(self, event):
        pass
    
    def mouse_button_down(self, event):
        pass


class ReplayMode(EventHandler):
    def key_down(self, event):
        if event.key == pygame.K_f:
            self.parent.flip_board()
        node = self.parent.node
        if event.key == pygame.K_LEFT:
            self.parent.node = node.parent or node
        if event.key == pygame.K_RIGHT:
            self.parent.make_random_move()


class PracticeMode(EventHandler):
    def __init__(self, parent, color):
        super().__init__(parent)
        self.active_square = None
        self.color = color
        if not color:
            self.parent.make_random_move()
    
    def key_down(self, event):
        if event.key == pygame.K_f:
            self.parent.flip_board()
        if event.key == pygame.K_r:
            # reset to root node
            self.parent.node = self.parent.node.game()
            if not self.color:
                self.parent.make_random_move()
    
    def mouse_button_down(self, event):
        x, y = event.pos
        file_index, rank_index = self.parent.pixel_to_square(x, y)
        square = chess.square(file_index, rank_index)
        if self.active_square is None:
            self.active_square = square
        else:
            move = chess.Move(self.active_square, square)
            if self.active_square == square:
                self.active_square = None
                return
            self.active_square = None
            self.check_move(move)
    
    def check_move(self, move):
        correct = False
        variations = self.parent.node.variations
        if not variations:
            print("variation ended")
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


class Window:
    def __init__(self):
        with open('pgn/jaenisch_gambit.pgn') as f:
            game = chess.pgn.read_game(f)
        self.node = game
        self.mode = PracticeMode(self, chess.BLACK)
        self.orientation = chess.BLACK
        self.surface = None
        self.font = None
        self.show_arrows = False
    
    def mainloop(self):
        pygame.init()
        self.surface = pygame.display.set_mode((SIZE+200, SIZE+100))
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
    
    def draw(self):
        self.surface.fill("#000000")  # clear
        board = self.node.board()
        board_svg = chess.svg.board(
            board,
            orientation=self.orientation,
            arrows=self.get_arrows(),
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
        self.draw_move_list()
        self.draw_comment()
    
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
            self.surface.blit(text_surface, (SIZE+15, total_height))
            total_height += text_surface.get_height()
    
    def draw_comment(self):
        comment_surface = self.font.render(
            self.node.comment.encode('latin-1'),
            False,
            "#ffffff",
            "#000000"
        )
        self.surface.blit(comment_surface, (0, SIZE + 15))
    
    def get_arrows(self) -> list:
        if not self.show_arrows:
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
        x = 15*BORDER + 45*file_index
        y = 15*BORDER + 45*rank_index
        return x, y
    
    def pixel_to_square(self, x, y):
        file_index = (x - 15*BORDER) // 45
        rank_index = (y - 15*BORDER) // 45
        if self.orientation:
            rank_index = 7 - rank_index
        else:
            file_index = 7 - file_index
        return file_index, rank_index


def main():
    Window().mainloop()


if __name__ == '__main__':
    main()
