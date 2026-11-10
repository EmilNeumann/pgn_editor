# coding: utf-8


import chess

import transpositions
from .core import Scrollable


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


class TreeView(Scrollable):
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root: TreeNode = root
        self.visible_nodes: list[TreeNode] = []

    @property
    def selected_node(self):
        return self.parent.selected_node

    def draw(self):
        super().draw()
        for node in self.visible_nodes:
            background = "#000000"
            if node is self.selected_node:
                background = "#0000ff"
            elif node.fen == self.selected_node.fen:
                background = "#7f007f"
            elif self.selected_node.is_descendant(node):
                background = "#00007f"
            elif node.game_node.comment:
                background = "#3f3f3f"
            text_surface = self.window.font.render(
                node.text,
                False,
                get_text_color_from_nags(node.game_node.nags),
                background
            )
            position = (
                node.position[0],
                node.position[1] - self.line_offset * self.window.char_height
            )
            self.surface.blit(text_surface, position)

    def update(self):
        """
        Determine which nodes are visible and where they are.
        """
        self.visible_nodes.clear()
        self.selected_node.make_visible()
        lines = get_lines(self.root, 0)
        self.line_count = len(lines)
        for line_index, line in enumerate(lines):
            indentation, tree_nodes = line
            y = line_index * self.window.char_height
            x = indentation * 2 * self.window.char_width
            for tree_node in tree_nodes:
                tree_node.position = (x, y)
                tree_node.text = tree_node.base_text
                if not tree_node.expanded and len(tree_node.children) > 1:
                    tree_node.text += f" ({len(tree_node.children)}"
                    tree_node.text += f"/{tree_node.get_subtree_lines()}/"
                    tree_node.text += f"{tree_node.get_subtree_size()})"
                tree_node.width = len(tree_node.text) * self.window.char_width
                tree_node.height = self.window.char_height
                self.visible_nodes.append(tree_node)
                x += tree_node.width + self.window.char_width

    def click(self, pos):
        x, y = pos
        for node in self.visible_nodes:
            node_x, node_y = node.position
            node_y -= self.line_offset * self.window.char_height
            if (x - node_x) in range(node.width) and (y - node_y) in range(node.height):
                self.parent.selected_node = node
                break


class TreeNode:
    def __init__(self, game_node, parent):
        self.game_node = game_node
        self.parent: TreeNode | None = parent
        self.expanded: bool = False
        self.base_text: str = ""
        self.fen: str = transpositions.shorten_fen(game_node.board().fen())
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
        # the following attributes are managed by the TreeView class
        self.text: str = self.base_text
        self.position: tuple[int, int] = (0, 0)
        self.width: int = 0
        self.height: int = 0
    
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
    
    def is_descendant(self, ancestor):
        if self.parent is None:
            return False
        return ancestor == self.parent or self.parent.is_descendant(ancestor)
