# coding: utf-8


import chess

import transpositions


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
        self.width = 0
        self.height = 0
    
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
            child.get_subtree_size()
            for child in self.children
        )
    
    def get_subtree_lines(self):
        return (len(self.children) == 0) + sum(
            child.get_subtree_lines()
            for child in self.children
        )
