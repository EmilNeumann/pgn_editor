# coding: utf-8

import random

import chess
import chess.pgn
import pygame

from src import config
from src import transpositions
from src.game_view import GameView
from src.ui import ReplayMode, TreeNode, get_lines, get_arrow_color_from_nags, get_text_color_from_nags


class Window:
    def __init__(self):
        self.orientation = chess.WHITE
        with open(config.OPENING_PGN) as f:
            self.root = chess.pgn.read_game(f)
            if self.root.headers['Black'] == config.PLAYER_NAME:
                self.orientation = chess.BLACK
        self.root = TreeNode(self.root, None)
        self.positions = {}
        transpositions.get_positions(self.root.game_node, self.positions)
        self.mode = ReplayMode(self)
        self.surface = None
        self.font = None
        self.font_size = config.FONT_SIZE
        self.font_type = config.FONT_TYPE
        self.visible_nodes = []
        self.selected_node = self.root
        self.treeview_pos = (config.BOARD_SIZE + config.BORDER_SIZE, 0)
        self.tree_text = []
        self.game_view = GameView(self)

    def mainloop(self):
        pygame.init()
        self.surface = pygame.display.set_mode(
            (config.BOARD_SIZE + 700, config.BOARD_SIZE + 500),
            flags=pygame.RESIZABLE,
        )
        self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self.update_treeview()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    self.handle_key(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mode.mouse_button_down(event)
            self.game_view.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_key(self, event):
        if event.key == pygame.K_F1:
            self.cycle_font_size()
        elif event.key == pygame.K_F2:
            self.cycle_font_type()
        else:
            self.mode.key_down(event)

    def cycle_font_size(self):
        index = config.FONT_SIZE_OPTIONS.index(self.font_size)
        next_index = (index + 1) % len(config.FONT_SIZE_OPTIONS)
        self.font_size = config.FONT_SIZE_OPTIONS[next_index]
        if self.surface is not None:
            self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self.refresh_tree_layout()

    def cycle_font_type(self):
        index = config.FONT_TYPE_OPTIONS.index(self.font_type)
        next_index = (index + 1) % len(config.FONT_TYPE_OPTIONS)
        self.font_type = config.FONT_TYPE_OPTIONS[next_index]
        if self.surface is not None:
            self.font = pygame.font.SysFont(self.font_type, self.font_size)
        self.refresh_tree_layout()

    def refresh_tree_layout(self):
        if self.selected_node is None:
            return
        self.update_treeview()

    def update_treeview(self): 
        self.visible_nodes.clear()
        self.selected_node.make_visible()
        lines = get_lines(self.root, 0)
        offset_x, offset_y = self.treeview_pos
        for line_index, line in enumerate(lines):
            indentation, tree_nodes = line
            y = offset_y + line_index * config.CHAR_HEIGHT
            x = offset_x + indentation * 2 * config.CHAR_WIDTH
            for tree_node in tree_nodes:
                tree_node.position = (x, y)
                tree_node.text = tree_node.base_text
                if not tree_node.expanded and len(tree_node.children) > 1:
                    tree_node.text += f' ({tree_node.get_subtree_size()})'
                if self.font is not None:
                    text_surface = self.font.render(tree_node.text, False, '#ffffff')
                    tree_node.width = text_surface.get_width()
                    tree_node.height = text_surface.get_height()
                else:
                    tree_node.width = len(tree_node.text) * config.CHAR_WIDTH
                    tree_node.height = config.CHAR_HEIGHT
                self.visible_nodes.append(tree_node)
                x += tree_node.width + config.CHAR_WIDTH

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
        x = config.BORDER_SIZE + config.SQUARE_SIZE * file_index
        y = config.BORDER_SIZE + config.SQUARE_SIZE * rank_index
        return x, y

    def pixel_to_square(self, x, y):
        file_index = (x - config.BORDER_SIZE) // config.SQUARE_SIZE
        rank_index = (y - config.BORDER_SIZE) // config.SQUARE_SIZE
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

    def get_arrow_color_from_nags(self, nags):
        return get_arrow_color_from_nags(nags)

    def get_text_color_from_nags(self, nags):
        return get_text_color_from_nags(nags)


from src.ui import PracticeMode
