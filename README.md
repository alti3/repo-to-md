# repo-to-md

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
    *   **Specify Directory:**
        ```bash
        ./repo_to_md.py /path/to/your/project
        ```
    *   **Output to File:**
        ```bash
        ./repo_to_md.py . --output project_docs.md
        # or short form:
        ./repo_to_md.py . -o project_docs.md
        ```
    *   **Output to Clipboard:**
        ```bash
        ./repo_to_md.py . --clipboard
        # or short form:
        ./repo_to_md.py . -c
        ```
    *   **Ignore Specific Directories:** (Uses default ignores + adds `logs` and `temp`)
        ```bash
        ./repo_to_md.py . --ignore-dir logs --ignore-dir temp
        ```
    *   **Ignore Specific Files:** (Uses default ignores + adds `.env` and `config.json`)
        ```bash
        ./repo_to_md.py . --ignore-file .env --ignore-file config.json
        ```
    *   **Ignore Specific Extensions:** (Uses default ignores + adds `.log` and `.tmp`)
        ```bash
        ./repo_to_md.py . --ignore-ext log --ignore-ext .tmp # Handles leading dot or not
        ```
    *   **Combining Ignores:**
        ```bash
        ./repo_to_md.py . -o out.md --ignore-dir build --ignore-file secrets.txt --ignore-ext bak
        ```
    *   **Get Help:**
        ```bash
        ./repo_to_md.py --help
        ```

## Features

1.  **Typer Integration:** Uses `typer.Typer()` and `@app.command()` for the CLI structure. Arguments and options are defined using type hints and `typer.Argument`/`typer.Option`. Typer handles help generation, type validation, and default values nicely.
2.  **Pathlib:** Consistently uses `pathlib.Path` for robust path manipulation. `resolve_path=True` in Typer options ensures absolute paths.
3.  **Type Hinting:** Uses type hints (`List`, `Optional`, `Set`, `Path`) throughout for clarity and correctness.
4.  **Specific Ignore Flags:** Implemented `--ignore-dir`, `--ignore-file`, and `--ignore-ext` as requested. These accept multiple values. Default ignore lists are used.
5.  **Ignoring Logic:** The `os.walk` loop now checks against the provided sets of ignored directories, files, and extensions. Directory ignoring uses the `topdown=True` approach to modify `dirnames` *in place*. Extension checking is case-insensitive and handles leading dots.
6.  **Error Handling:** Uses `typer.Exit(code=1)` for exiting on errors. Prints error/warning messages to `stderr` using `typer.echo(..., err=True)`. Includes checks for `pyperclip` availability and file I/O errors. File reading uses `errors='ignore'` and catches potential `OSError`.
7.  **Binary File Handling:** The `is_likely_binary` check remains, using extensions and a null-byte check.
8.  **Structure Output:** The initial file structure listing is generated during the walk and sorted before being added to the output. The example output format is maintained.
