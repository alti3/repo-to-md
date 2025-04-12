#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Optional

import typer

# Attempt to import pyperclip, but make it optional
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    pyperclip = None # Define it as None if not available


# --- Configuration ---
# Files/directories/extensions to ignore by default
DEFAULT_IGNORE_DIRS: set[str] = {
    ".git", "__pycache__", ".venv", ".vscode", ".idea", "node_modules",
    "build", "dist", "wheels", ".egg-info",
}
DEFAULT_IGNORE_FILES: set[str] = {
    ".DS_Store", "Thumbs.db"
}
DEFAULT_IGNORE_EXTS: set[str] = {
    ".pyc", ".pyo", ".pyd", ".so", ".o", ".a", ".dylib", ".lock"
}

# File extensions often considered binary (can be approximate)
# We'll ignore these by default unless overridden by not ignoring them explicitly
BINARY_EXTENSIONS: set[str] = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".tif", ".tiff", ".webp",
    # Archives
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp",
    # Executables/Libraries
    ".exe", ".dll", ".so", ".dylib", ".app", ".bin",
    # Compiled code / Data
    ".o", ".a", ".lib", ".class", ".jar", ".obj",
    # Media
    ".mp3", ".wav", ".ogg", ".flac", ".aac",
    ".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv",
    # Databases / Other
    ".sqlite", ".db", ".mdb", ".dbf",
    ".lock", # Often lock files are not human-readable text
    ".woff", ".woff2", ".eot", ".ttf", ".otf", # Fonts
}

SEPARATOR = "-" * 80

# --- Helper Functions ---

def is_likely_binary(file_path: Path) -> bool:
    """Guess if a file is binary based on extension or content."""
    if file_path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        # Try reading a small chunk to detect null bytes, common in binaries
        with open(file_path, "rb") as f:
            chunk = f.read(1024) # Read first 1KB
            if b'\x00' in chunk:
                return True
    except Exception:
        # If reading fails, treat it cautiously as potentially binary or problematic
        return True
    return False

def format_file_content(file_path: Path, root_dir: Path) -> str:
    """Formats the content of a single file for Markdown output."""
    try:
        relative_path = file_path.relative_to(root_dir)
        # Use forward slashes for cross-platform consistency in output
        relative_path_str = "/" + str(relative_path.as_posix())
    except ValueError:
        # Should not happen if logic is correct, but handle defensively
        relative_path_str = f"/{file_path.name}"

    output_lines = [f"{relative_path_str}:", SEPARATOR]

    if is_likely_binary(file_path):
        output_lines.append("    [Skipping binary file content]")
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if not lines:
                    output_lines.append("    [Empty file]")
                else:
                    max_line_num_width = len(str(len(lines)))
                    for i, line in enumerate(lines, start=1):
                        line_content = line.rstrip('\n\r') # Strip CR and LF
                        output_lines.append(f"{i:>{max_line_num_width}} | {line_content}")
        except OSError as e:
            output_lines.append(f"    [Error reading file: {e}]")
        except Exception as e: # Catch unexpected errors during read
             output_lines.append(f"    [Unexpected error reading file: {e}]")

    output_lines.append(SEPARATOR)
    return "\n".join(output_lines)

# --- Core Logic ---

def generate_markdown(
    root_dir: Path,
    ignore_dirs: set[str],
    ignore_files: set[str],
    ignore_exts: set[str],
) -> str:
    """Walks the directory and generates the Markdown string."""
    all_files_to_process: list[Path] = []
    structure_lines: list[str] = []

    # Normalize ignore extensions (ensure they start with '.')
    normalized_ignore_exts = { f".{ext.lstrip('.')}".lower() for ext in ignore_exts }

    for dirpath_str, dirnames, filenames in os.walk(root_dir, topdown=True):
        current_path = Path(dirpath_str)
        relative_dir_path = current_path.relative_to(root_dir)

        # --- Filtering Logic ---
        # Filter directories based on ignore patterns in-place
        dirs_to_remove = {
            d for d in dirnames
            if d in ignore_dirs or (current_path / d) in ignore_dirs # Check full path too? No, simple name check is common
        }
        dirnames[:] = [d for d in dirnames if d not in dirs_to_remove] # Modify in-place

        # Add current directory to structure (if not root)
        # depth = len(relative_dir_path.parts)
        # indent = "  " * depth + "├── " if depth > 0 else ""
        # if depth > 0: # Don't list the root itself in the structure
        #     structure_lines.append(f"{indent}/{relative_dir_path.name}/")

        # Process files
        for filename in sorted(filenames): # Sort files within dir
            file_full_path = current_path / filename
            file_ext_lower = file_full_path.suffix.lower()

            # Check ignore conditions
            if filename in ignore_files:
                continue
            if file_ext_lower in normalized_ignore_exts:
                continue

            # Add to structure list and processing list
            relative_file_path = file_full_path.relative_to(root_dir)
            # Use forward slashes for display
            structure_lines.append(f"└── /{relative_file_path.as_posix()}")
            all_files_to_process.append(file_full_path)

        # Sort dirnames for consistent structure output (optional, but nice)
        dirnames.sort()
        for dirname in dirnames:
             relative_subdir_path = relative_dir_path / dirname
             structure_lines.append(f"├── /{relative_subdir_path.as_posix()}/")


    # --- Generate Output String ---
    output_parts: list[str] = []

    # Part 1: The file/directory listing (simplified flat list based on example)
    if structure_lines:
        output_parts.extend(sorted(structure_lines)) # Sort the final structure list
        output_parts.append("\n") # Add space before content

    # Part 2: The file contents
    all_files_to_process.sort() # Sort all collected files by full path
    for file_path in all_files_to_process:
        try:
            file_content_md = format_file_content(file_path, root_dir)
            output_parts.append(file_content_md)
            output_parts.append("\n") # Add space between file blocks
        except Exception as e:
             # Gracefully handle errors for a single file
             typer.echo(f"Warning: Could not process file '{file_path}': {e}", err=True)


    return "".join(output_parts).strip() # Join all parts


# --- Typer App ---
app = typer.Typer(
    help="Generate a Markdown file documenting files/code in a directory.",
    add_completion=False
)

@app.command()
def main(
    repo_path: Path = typer.Argument(
        ...,  # Ellipsis means it's required
        help="The root directory path of the repository/project.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True, # Converts to absolute path
    ),
    output_file: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Optional path to write the Markdown output to a file.",
        writable=True,
        resolve_path=True, # Ensure parent dir exists before write attempt
    ),
    to_clipboard: bool = typer.Option(
        False, "--clipboard", "-c",
        help="Optional flag to copy the Markdown output to the clipboard.",
    ),
    ignore_dir: list[str] = typer.Option(
        list(DEFAULT_IGNORE_DIRS), # Use default list directly
        "--ignore-dir",
        help="Directory name(s) to ignore (e.g., 'node_modules'). Can be used multiple times.",
        show_default=False, # Avoid showing the long default list in help
    ),
    ignore_file: list[str] = typer.Option(
        list(DEFAULT_IGNORE_FILES),
        "--ignore-file",
        help="File name(s) to ignore (e.g., '.env'). Can be used multiple times.",
         show_default=False,
    ),
    ignore_ext: list[str] = typer.Option(
        list(DEFAULT_IGNORE_EXTS),
        "--ignore-ext",
        help="File extension(s) to ignore (e.g., 'log', '.tmp'). Can be used multiple times.",
         show_default=False,
    ),
):
    """
    Generates Markdown documentation for a repository directory structure and file contents.
    """
    # --- Initial Checks ---
    if to_clipboard and not PYPERCLIP_AVAILABLE:
        typer.echo("Error: --clipboard requires the 'pyperclip' library.", err=True)
        typer.echo("Install it using: pip install pyperclip", err=True)
        raise typer.Exit(code=1)

    # Combine provided ignores with defaults if needed (Typer handles defaults well)
    # Convert lists to sets for efficient lookup during walk
    ignore_dirs_set = set(ignore_dir)
    ignore_files_set = set(ignore_file)
    ignore_exts_set = set(ignore_ext)

    # --- Generate the Markdown ---
    typer.echo(f"Processing directory: {repo_path}", err=True) # Info message to stderr
    try:
        markdown_output = generate_markdown(
            repo_path,
            ignore_dirs_set,
            ignore_files_set,
            ignore_exts_set,
        )
    except Exception as e:
        typer.echo(f"\nAn unexpected error occurred during Markdown generation: {e}", err=True)
        # Consider adding more detailed traceback logging here if needed for debugging
        raise typer.Exit(code=1)

    # --- Handle Output ---
    if output_file:
        try:
            # Ensure parent directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_output)
            typer.echo(f"Markdown output successfully written to: {output_file}", err=True)
        except IOError as e:
            typer.echo(f"Error: Could not write to output file '{output_file}': {e}", err=True)
            raise typer.Exit(code=1)
        except Exception as e:
             typer.echo(f"Error: An unexpected error occurred writing to file '{output_file}': {e}", err=True)
             raise typer.Exit(code=1)

    elif to_clipboard:
        try:
            if pyperclip: # Double check availability
                pyperclip.copy(markdown_output)
                typer.echo("Markdown output copied to clipboard.", err=True)
            else:
                 # This case should be caught earlier, but as a safeguard
                 typer.echo("Error: pyperclip not available for clipboard operation.", err=True)
                 raise typer.Exit(code=1)
        except Exception as e: # Catch potential pyperclip errors
            typer.echo(f"Error: Could not copy to clipboard: {e}", err=True)
            raise typer.Exit(code=1)

    else:
        # Default to stdout
        try:
            # Use typer.echo to print the final result to stdout
            typer.echo(markdown_output)
        except Exception as e:
            # This might happen if stdout is closed or has encoding issues
            typer.echo(f"Error printing output to stdout: {e}", file=sys.stderr)
            raise typer.Exit(code=1)

    typer.echo("Processing complete.", err=True)


if __name__ == "__main__":
    app()