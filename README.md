# pgn_editor
A desktop program for viewing and editing PGN files (with a focus on opening preparation)

## Development Status
This project is still in the pre-version-numbers alpha.

## Prerequisites
- Python3.10+ (may also work with older versions, but they reached EOL)
- [`chess`](https://github.com/niklasf/python-chess) & [`pygame`](https://github.com/pygame/pygame)
  - also works with [`pygame-ce`](https://github.com/pygame-community/pygame-ce) and may depend on it in the future
- the [Sourcecode Pro](https://github.com/adobe-fonts/source-code-pro) font (will be included in future versions)

## TBD
- Editing functionality
  - adding / deleting variations
  - moving variations up / down
  - editing comments and NAGs (!, ?, !!, ??, !?, ?!)
  - editing PGN headers
- File dialogs
  - loading a game in a new tab
  - loading a game into the current tree, merging them
  - saving the current tree entirely
  - saving a subtree
- Menubar & context menu
- Clipboard access
- translations
- Lichess player database access
- interface for UCI engines like Stockfish
- "Open with pgn_editor" entry in file explorer context menu

## License
GNU AGPLv3
