# coding: utf-8


import chess.pgn


def get_move_list(node):
    pgn = str(chess.pgn.Game.from_board(node.board()))
    return pgn.rpartition("\n")[-1]


def show_node_info(node):
    moves = get_move_list(node)
    print(
        moves,
        f"{len(node.variations)} variations",
        f"comment: {node.comment}",
        sep="\t"
    )


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
            show_node_info(node)
        print()


def show_malformed_transpositions(positions: dict[str, list]):
    for fen, nodes in positions.items():
        if len(nodes) <= 1:
            continue
        mainlines = 0
        comments = 0
        for node in nodes:
            mainlines += bool(node.variations)
            comments += node.comment.startswith('transposes into ')
            comments += node.comment == 'repeats the position'
        if mainlines > 1 or comments < len(nodes) - 1:
            print(fen)
            for node in nodes:
                show_node_info(node)
            if mainlines > 1:
                print(f"too many mainlines ({mainlines})")
            if comments < len(nodes) - 1:
                print("missing transposition comment(s)")
            print()
        elif not mainlines:
            print(fen)
            for node in nodes:
                show_node_info(node)
            print("warning: no mainline")
            print()


def main():
    with open('pgn/jaenisch_gambit.pgn') as f:
        game = chess.pgn.read_game(f)
    positions = {}
    get_positions(game, positions)
    # show_transpositions(positions)
    show_malformed_transpositions(positions)


if __name__ == '__main__':
    main()
