import os
import sys
from pathlib import Path
from datetime import datetime

# Root directory of the repository
ROOT_DIR = Path(__file__).resolve().parent.parent

# Directories to skip entirely (will not be traversed)
EXCLUDE_DIRS = {
    'node_modules',
    '.next',
    '.git',
    '.github',
    '.venv',
    'venv',
    'env',
    '__pycache__',
    '.pytest_cache',
    '.turbo',
    '.kilo',
    'dist',
    'build',
    'coverage',
    '.idea',
    '.vscode',
    'frontend'  # Default empty Next.js boilerplate folder
}

# Binary & non-source extensions to skip
EXCLUDE_EXTENSIONS = {
    # Images / Media
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp', '.bmp', '.tiff',
    '.mp4', '.mp3', '.wav', '.mov', '.avi', '.mkv',
    # Fonts
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    # Documents / Binaries
    '.pdf', '.exe', '.dll', '.bin', '.so', '.dylib', '.zip', '.tar', '.gz', '.7z',
    # Databases / Compiled / Caches
    '.db', '.sqlite', '.sqlite3', '.pyc', '.pyo', '.pyd'
}

# Specific files to skip
EXCLUDE_FILES = {
    'package-lock.json',
    'yarn.lock',
    'pnpm-lock.yaml',
    'cygrc.db',
    'combined_codebase.txt',
    'combined_code.txt',
    'all_code.txt',
    'combine_code.bat',
    'export_codebase.bat'
}

def is_text_file(filepath: Path) -> bool:
    """Check if file can be read as UTF-8 text."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, PermissionError, OSError):
        return False

def collect_files():
    collected = []
    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        # Prune excluded directories in-place so os.walk does not recurse into them
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith('.')]

        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in EXCLUDE_EXTENSIONS or fname in EXCLUDE_FILES or fname.endswith('.log'):
                continue

            full_path = Path(dirpath) / fname
            rel_path = full_path.relative_to(ROOT_DIR).as_posix()

            if is_text_file(full_path):
                collected.append((rel_path, full_path))

    # Sort files alphabetically by relative path
    collected.sort(key=lambda x: x[0])
    return collected

def combine_code(output_path: Path):
    print("Scanning project files...")
    files = collect_files()
    print(f"Found {len(files)} source code files.")

    total_lines = 0
    file_contents = []

    for rel_path, full_path in files:
        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
                total_lines += lines
                file_contents.append((rel_path, content, lines))
        except Exception as e:
            print(f"Skipping {rel_path}: {e}")

    print(f"Writing combined file to {output_path.name} ({total_lines:,} total lines)...")

    with open(output_path, 'w', encoding='utf-8') as out:
        # Header
        out.write("=" * 80 + "\n")
        out.write("CYGRC PLATFORM — COMBINED CODEBASE EXPORT\n")
        out.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.write(f"Total Files: {len(file_contents)}\n")
        out.write(f"Total Lines of Code: {total_lines:,}\n")
        out.write("=" * 80 + "\n\n")

        # Table of Contents
        out.write("TABLE OF CONTENTS\n")
        out.write("-" * 80 + "\n")
        for idx, (rel_path, _, lines) in enumerate(file_contents, 1):
            out.write(f"{idx:3d}. [{rel_path}] ({lines} lines)\n")
        out.write("-" * 80 + "\n\n")

        # File contents
        for idx, (rel_path, content, lines) in enumerate(file_contents, 1):
            out.write("=" * 80 + "\n")
            out.write(f"[{idx}/{len(file_contents)}] FILE: {rel_path}\n")
            out.write(f"LINES: {lines}\n")
            out.write("=" * 80 + "\n")
            out.write(content)
            if not content.endswith('\n'):
                out.write('\n')
            out.write("\n\n")

    print(f"Done! Combined codebase saved to: {output_path}")

if __name__ == '__main__':
    out_file = ROOT_DIR / "combined_codebase.txt"
    combine_code(out_file)
