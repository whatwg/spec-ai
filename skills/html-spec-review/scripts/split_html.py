#!/usr/bin/env python3
import hashlib
import os
import re
import sys

SOURCE_HASH_FILE = '.source-hash'


def _hash_text(text):
    """Return the SHA-256 hex digest of text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _write_source_hash(split_dir, text):
    """Record the hash of source corresponding to split_dir's current contents."""
    with open(os.path.join(split_dir, SOURCE_HASH_FILE), 'w', encoding='utf-8') as f:
        f.write(_hash_text(text) + '\n')


def _resolve_git_common_dir(start_dir):
    """Find the enclosing repository's root and common git dir, or None if not in git."""
    cur = os.path.abspath(start_dir)
    while True:
        dotgit = os.path.join(cur, '.git')
        if os.path.isdir(dotgit):
            return cur, dotgit
        if os.path.isfile(dotgit):
            with open(dotgit, 'r', encoding='utf-8') as f:
                line = f.readline().strip()
            if line.startswith('gitdir:'):
                git_dir = os.path.abspath(os.path.join(cur, line[len('gitdir:'):].strip()))
                commondir_file = os.path.join(git_dir, 'commondir')
                if os.path.isfile(commondir_file):
                    with open(commondir_file, 'r', encoding='utf-8') as f:
                        common = f.readline().strip()
                    git_dir = os.path.abspath(os.path.join(git_dir, common))
                return cur, git_dir
            return None
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def _ensure_git_excluded(output_dir):
    """Ensure output_dir is listed in the enclosing git repository's info/exclude."""
    found = _resolve_git_common_dir(output_dir)
    if not found:
        return
    repo_root, common_dir = found
    rel_path = os.path.relpath(os.path.abspath(output_dir), repo_root).replace(os.sep, '/')
    pattern = f'/{rel_path}/'
    exclude_path = os.path.join(common_dir, 'info', 'exclude')

    existing = ''
    if os.path.isfile(exclude_path):
        with open(exclude_path, 'r', encoding='utf-8') as f:
            existing = f.read()
        existing_lines = {line.strip() for line in existing.splitlines()}
        if pattern in existing_lines or pattern.rstrip('/') in existing_lines:
            return

    try:
        os.makedirs(os.path.dirname(exclude_path), exist_ok=True)
        prefix = '\n' if existing and not existing.endswith('\n') else ''
        with open(exclude_path, 'a', encoding='utf-8') as f:
            f.write(f'{prefix}{pattern}\n')
    except OSError as exc:
        print(f"Warning: could not update {exclude_path}: {exc}", file=sys.stderr)


def split_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all h2 tags
    # The first section is everything before the first h2
    pattern = re.compile(r'(?=<h2\b)', re.IGNORECASE)
    parts = pattern.split(content)

    base_dir = os.path.dirname(os.path.abspath(file_path))
    output_dir = os.path.join(base_dir, 'split_source')
    os.makedirs(output_dir, exist_ok=True)
    _ensure_git_excluded(output_dir)

    # Clear directory first
    for f in os.listdir(output_dir):
        if f.endswith('.html'):
            os.remove(os.path.join(output_dir, f))

    for i, part in enumerate(parts):
        if i == 0:
            filename = '00_start.html'
        else:
            # Try to find split-filename="..." or id="..."
            name_match = re.search(r'split-filename="([^"]+)"', part)
            if not name_match:
                name_match = re.search(r'id="([^"]+)"', part)

            if name_match:
                name = name_match.group(1)
            else:
                name = 'section'
            filename = f'{i:02d}_{name}.html'

        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(part)

    _write_source_hash(output_dir, content)
    print(f"Successfully split into {len(parts)} files in {output_dir}")


def concat_files(file_path):
    base_dir = os.path.dirname(os.path.abspath(file_path))
    split_dir = os.path.join(base_dir, 'split_source')

    if not os.path.exists(split_dir):
        print("Split directory not found.")
        sys.exit(1)

    files = sorted([f for f in os.listdir(split_dir) if f.endswith('.html')])
    if not files:
        print("No split files found.")
        sys.exit(1)

    hash_path = os.path.join(split_dir, SOURCE_HASH_FILE)
    if os.path.isfile(hash_path) and os.path.isfile(file_path):
        with open(hash_path, 'r', encoding='utf-8') as f:
            expected_hash = f.read().strip()
        with open(file_path, 'r', encoding='utf-8') as f:
            current_hash = _hash_text(f.read())
        if current_hash != expected_hash:
            print(
                f"Error: {file_path} has changed since {split_dir} was generated; "
                "re-run 'split' before editing and concatenating.",
                file=sys.stderr,
            )
            sys.exit(1)

    chunks = []
    for f in files:
        with open(os.path.join(split_dir, f), 'r', encoding='utf-8') as infile:
            chunks.append(infile.read())
    combined = ''.join(chunks)

    with open(file_path, 'w', encoding='utf-8') as outfile:
        outfile.write(combined)

    _write_source_hash(split_dir, combined)
    print(f"Successfully concatenated {len(files)} files into {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 split_html.py <split|concat> <file_path>")
        sys.exit(1)

    action = sys.argv[1]
    file_path = sys.argv[2]

    if action == "split":
        split_file(file_path)
    elif action == "concat":
        concat_files(file_path)
    else:
        print("Unknown action. Use 'split' or 'concat'")
        sys.exit(1)
