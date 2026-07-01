# Portable Game Notation Editor

A small Python application for exploring and reviewing chess games from PGN files. The project renders a board, supports move navigation, and shows a tree-style view of the game variations.

## Features

- Load chess games from PGN files in the pgn directory
- Display the current board position with pygame
- Navigate through moves and variations
- Highlight and inspect comments and move annotations
- Practice mode for replaying selected variations

## Project Structure

- main.py: application entry point
- src/: Python package containing the main application modules
  - config.py: shared constants and configuration
  - ui.py: tree nodes, event handlers, and game modes
  - game_view.py: rendering logic for the board and UI
  - window.py: main window and game loop
  - transpositions.py: helpers for transposition analysis
- pgn/: sample PGN game files
- tests/: regression tests for the renderer

## Requirements

Install the dependencies in the project virtual environment:

```bash
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install python-chess pygame
```

## Run the application

From the project root:

```bash
./.venv/bin/python main.py
```

## Run tests

```bash
./.venv/bin/python -m unittest -q tests.test_game_view
```

## Notes

The current project is focused on visualization and interaction with PGN game trees. It is a lightweight tool for studying openings and variations rather than a full chess engine.
