# coding: utf-8


import datetime
import os.path

import chess
import chess.pgn
import pygame

from widgets.boardview import BoardView
from widgets.treeview import TreeNode


SIZE = 400


class Window:
    def __init__(self):
        self.surface = pygame.display.set_mode((SIZE, SIZE), flags=pygame.RESIZABLE)
        self.font = pygame.font.SysFont("sourcecodepro", 16)
        today = datetime.date.today()
        filename = f'{today}.pgn'
        path = os.path.join('pgn', filename)
        if os.path.exists(path):
            with open(os.path.join('pgn', filename)) as f:
                self.game = chess.pgn.read_game(f)
            pygame.display.set_caption(filename)
        else:
            self.game = chess.pgn.Game()
            pygame.display.set_caption("New Game")
        self.selected_node = TreeNode(self.game, None)
        self.show_arrows = True
        self.board_view = BoardView(self)

    def mainloop(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_button_down(event)
                if event.type == pygame.KEYDOWN:
                    self.key_down(event)
            self.draw()
            clock.tick(60)
            pygame.display.flip()

    def draw(self):
        self.surface.fill("#000000")
        self.board_view.draw()
        self.surface.blit(self.board_view.surface, self.board_view.position)

    def mouse_button_down(self, event):
        x, y = event.pos
        rel_x = x - self.board_view.x
        rel_y = y - self.board_view.y
        if rel_x in range(self.board_view.width) and rel_y in range(self.board_view.height):
            self.board_view.click((rel_x, rel_y))

    def key_down(self, event):
        if event.key == pygame.K_LEFT:
            if self.selected_node.parent is not None:
                self.selected_node = self.selected_node.parent
        if event.key == pygame.K_RIGHT:
            if len(self.selected_node.children) > 0:
                self.selected_node = self.selected_node.children[0]
        if event.key == pygame.K_f:
            self.board_view.orientation = not self.board_view.orientation
        if event.key == pygame.K_s:
            today = datetime.date.today()
            filename = f"{today}.pgn"
            with open(os.path.join('pgn', filename), 'w') as f:
                self.game.accept(chess.pgn.FileExporter(f))
            pygame.display.set_caption(f"saved {filename}")
        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
            if self.selected_node.parent is not None:
                node = self.selected_node
                self.selected_node = node.parent
                self.selected_node.children.remove(node)
                self.selected_node.game_node.variations.remove(node.game_node)
                pygame.display.set_caption("changed")

    def process_move(self, move):
        for child_node in self.selected_node.children:
            if child_node.game_node.move == move:
                self.selected_node = child_node
                break
        else:
            game_node = self.selected_node.game_node
            if game_node.board().is_legal(move):
                child_game_node = game_node.add_variation(move)
                child_tree_node = TreeNode(child_game_node, self.selected_node)
                self.selected_node.children.append(child_tree_node)
                self.selected_node = child_tree_node
                pygame.display.set_caption("changed")


def main():
    pygame.init()
    Window().mainloop()
    pygame.quit()


if __name__ == '__main__':
    main()
