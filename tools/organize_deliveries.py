#!/usr/bin/env python3
"""Relocate registered deliveries without changing bytes or breaking old paths.

The local JSON manifest has destination_root and files with source, destination,
sha256, and optional bytes. Default is a read-only preflight; --apply relocates
on the same filesystem and leaves compatibility symlinks; --verify checks both.
Never put private delivery manifests or their media in Git.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def preflight(manifest):
    root = Path(manifest['destination_root']).resolve()
    checked, sources, destinations = [], set(), set()
    for row in manifest['files']:
        source, destination = Path(row['source']).absolute(), Path(row['destination']).absolute()
        resolved = destination.resolve()
        if root not in resolved.parents or source == destination:
            raise ValueError('Destination must be a file under destination_root')
        if source in sources or destination in destinations:
            raise ValueError('Duplicate source or destination')
        sources.add(source)
        destinations.add(destination)
        if not source.is_file():
            raise ValueError(f'Missing source: {source}')
        if sha256(source) != row['sha256'] or ('bytes' in row and source.stat().st_size != row['bytes']):
            raise ValueError(f'Delivery checksum/size mismatch: {source}')
        already = source.is_symlink() and source.resolve() == resolved and destination.is_file()
        if os.path.lexists(destination) and not already:
            raise ValueError(f'Refusing destination overwrite: {destination}')
        if source.is_symlink() and not already:
            raise ValueError(f'Refusing to move an unrelated source symlink: {source}')
        ancestor = destination.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        if source.stat().st_dev != ancestor.stat().st_dev:
            raise ValueError('Use a separately verified copy workflow for another filesystem')
        checked.append((source, destination, already))
    if not checked:
        raise ValueError('No deliveries registered')
    if sources & destinations:
        raise ValueError('A destination overlaps another registered source')
    return checked


def relocate(manifest):
    checked = preflight(manifest)  # Verify the entire batch before the first move.
    for source, destination, already in checked:
        if already:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        if os.path.lexists(destination):
            raise ValueError(f'Destination appeared after preflight: {destination}')
        source.rename(destination)
        try:
            source.symlink_to(destination)
        except BaseException:
            destination.rename(source)
            raise
    return verify(manifest)


def verify(manifest):
    checked = preflight(manifest)
    if not all(already for _, _, already in checked):
        raise ValueError('Some deliveries have not been relocated with compatibility links')
    return {'verified': len(checked), 'sha256_verified': True, 'legacy_links_verified': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    if args.apply:
        result = relocate(manifest)
    elif args.verify:
        result = verify(manifest)
    else:
        result = {'preflight_verified': len(preflight(manifest)), 'modified': False}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
