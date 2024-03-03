# coding: utf-8


from enum import StrEnum


class PLAYER(StrEnum):
    BLACK = "b"
    WHITE = "w"


class Board:
    def __init__(self):
        self.squares = []
        self.castling = []
        self.en_passant = ""
        self.player = PLAYER.WHITE
        # for the 50 move rule
        # resets when a pawn is pushed or sth is captured
        self.reversible_moves = 0
        self.current_move = 1  # increments when black made a move
    
    def make_move(self, move: str):
        pass
    
    def is_check(self) -> bool:
        pass
    
    def is_checkmate(self) -> bool:
        pass
    
    def is_stalemate(self) -> bool:
        pass
    
    def get_fen(self) -> str:
        pass
    
    def get_legal_moves(self):
        pass
    
    def get_square(self, pos: str):
        pass
