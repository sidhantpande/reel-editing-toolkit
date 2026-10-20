"""Verify a user-approved delivery and protect its version from render overwrite."""
import argparse
import hashlib
import json
from pathlib import Path


def assert_unlocked(project, preflight=False):
    if (Path(project) / 'approval-lock.json').exists() and not preflight:
        raise RuntimeError('This delivery is approved and locked. Create a new version for changes; --preflight remains available.')


def verify_lock(manifest):
    doc = json.loads(Path(manifest).read_text())
    checked = []
    for row in doc['files']:
        path = Path(row['path'])
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        if h.hexdigest() != row['sha256']:
            raise ValueError(f'Approved export checksum mismatch: {path}')
        if row.get('bytes') is not None and path.stat().st_size != row['bytes']:
            raise ValueError(f'Approved export byte count mismatch: {path}')
        checked.append(dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size))
    if not checked:
        raise ValueError('Approval manifest has no exports')
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    print(json.dumps({'status': 'Approved exports verified', 'files': verify_lock(args.manifest)}, indent=2))


if __name__ == '__main__':
    main()
