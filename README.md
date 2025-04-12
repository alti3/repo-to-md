# repo-to-md

A command-line tool to generate a single Markdown file that concatenates the structure and content of a specified directory. Useful for providing context to Large Language Models (LLMs) or creating simple project documentation.

## Features
- Recursively scans a directory.
- Outputs a tree-like structure of the directory (using relative paths).
- Includes the content of text files, formatted with line numbers.
- Automatically detects and skips likely binary files.
- Allows ignoring specific directories, files, and extensions via command-line options.
- Provides sensible default ignores for common development artifacts (e.g., `.git`, `node_modules`, `.pyc`).
- Output can be directed to stdout (default), a file (`-o`), or the system clipboard (`-c`).
- Uses `typer` for a user-friendly command-line interface.

## How to Use

1.  **Install Dependencies:**
    ```bash
    uv sync
    ```
2.  **Make Executable (Optional):**
    ```bash
    chmod +x repo_to_md.py
    ```
3.  **Run:** (Examples assume it's executable, otherwise use `python repo_to_md.py ...`)

    *   **Basic Usage (Output to stdout, current directory):**
        ```bash
        ./repo_to_md.py .
        ```
        or
        ```bash
        uvx repo_to_md.py .
        ```
    *   **Specify Directory:**
        ```bash
        ./repo_to_md.py /path/to/your/project
        ```
        or
        ```bash
        uvx repo_to_md.py /path/to/your/project
        ```
    *   **Output to File:**
        ```bash
        ./repo_to_md.py . --output project_docs.md
        # or short form:
        ./repo_to_md.py . -o project_docs.md
        ```
        or
        ```bash
        uvx repo_to_md.py . -o project_docs.md
        ```
    *   **Output to Clipboard:**
        ```bash
        ./repo_to_md.py . --clipboard
        # or short form:
        ./repo_to_md.py . -c
        ```
        or
        ```bash
        uvx repo_to_md.py . -c
        ```
    *   **Ignore Specific Directories:** (Uses default ignores + adds `logs` and `temp`)
        ```bash
        ./repo_to_md.py . --ignore-dir logs --ignore-dir temp
        ```
        or
        ```bash
        uvx repo_to_md.py . --ignore-dir logs --ignore-dir temp
        ```
    *   **Ignore Specific Files:** (Uses default ignores + adds `.env` and `config.json`)
        ```bash
        ./repo_to_md.py . --ignore-file .env --ignore-file config.json
        ```
        or
        ```bash
        uvx repo_to_md.py . --ignore-file .env --ignore-file config.json
        ```
    *   **Ignore Specific Extensions:** (Uses default ignores + adds `.log` and `.tmp`)
        ```bash
        ./repo_to_md.py . --ignore-ext log --ignore-ext .tmp # Handles leading dot or not
        ```
        or
        ```bash
        uvx repo_to_md.py . --ignore-ext log --ignore-ext .tmp # Handles leading dot or not
        ```
    *   **Combining Ignores:**
        ```bash
        ./repo_to_md.py . -o out.md --ignore-dir build --ignore-file secrets.txt --ignore-ext bak
        ```
        or
        ```bash
        uvx repo_to_md.py . -o out.md --ignore-dir build --ignore-file secrets.txt --ignore-ext bak
        ```
    *   **Get Help:**
        ```bash
        ./repo_to_md.py --help
        ```
        or
        ```bash
        uvx repo_to_md.py --help
        ```

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.