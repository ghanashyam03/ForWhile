# ForWhile Syntax Highlighting for VS Code

This extension provides syntax highlighting and language configuration support for the **ForWhile** world-building programming language.

## Features

* **Syntax Highlighting**: Full color schemes for all ForWhile keywords (`creature`, `action`, `when born`, `the world remembers`, `whenever`, `on each tick`, etc.).
* **Code Blocks**: Auto-closing parentheses, double quotes, and comments configuration.

## Installation for Development

To test the extension locally:

1. Copy the `editors/vscode` directory to your VS Code extensions directory:
   * **Windows**: `%USERPROFILE%\.vscode\extensions\forwhile-syntax`
   * **macOS / Linux**: `~/.vscode/extensions/forwhile-syntax`
2. Restart or reload VS Code.

To package as a `.vsix` file for direct installation:
```bash
cd editors/vscode
npm install -g @vscode/vsce
vsce package
```
Then install the `.vsix` file using VS Code's command palette: `Extensions: Install from VSIX...`.
