# coding: utf-8


import chess.pgn


def get_positions(node, positions: dict[str, list]):
    fen = node.board().board_fen()
    positions[fen] = positions.get(fen, [])
    positions[fen].append(node)
    for child_node in node.variations:
        get_positions(child_node, positions)


def show_transpositions(positions: dict[str, list]):
    for fen, nodes in positions.items():
        if len(nodes) <= 1:
            continue
        print(fen)
        for node in nodes:
            pgn = str(chess.pgn.Game.from_board(node.board()))
            moves = pgn.rpartition("\n")[-1]
            print(
                moves,
                f"{len(node.variations)} variations",
                f"comment: {node.comment}",
                sep="\t"
            )
        print()


def main():
    with open('pgn/jaenisch_gambit.pgn') as f:
        game = chess.pgn.read_game(f)
    positions = {}
    get_positions(game, positions)
    show_transpositions(positions)


if __name__ == '__main__':
    main()
