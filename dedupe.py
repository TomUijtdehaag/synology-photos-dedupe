import os
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(prog="Synology Photos Dedupe")

    parser.add_argument("dir")  # positional argument
    parser.add_argument("dest")
    parser.add_argument("-d", "--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    # source dir
    dir = Path(args.dir)

    # destination dir
    dest = Path(args.dest)

    duplicates = list_duplicates(dir)

    if args.verbose:
        print_duplicates(duplicates)

    print_stats(duplicates)

    if not args.dry_run:
        dest.mkdir(exist_ok=True)
        move_duplicates(duplicates, dest)


def print_stats(duplicates):
    total_dupes = 0
    max_dupes = 0
    for files in duplicates.values():
        total_dupes += len(files)

        if len(files) > max_dupes:
            max_dupes = len(files)

    print(
        f"Found dupes of {len(duplicates)} files. Total: {total_dupes}. Max: {max_dupes}"
    )


def list_duplicates(dir: Path):
    filenames = {}
    for path in dir.glob("**/*"):
        if not path.is_file():
            continue
        paths = filenames.get(path.name, [])
        paths.append(path)
        filenames[path.name] = paths

    return {
        name: sorted(paths, key=lambda x: x.stat().st_size)
        for name, paths in filenames.items()
        if len(paths) > 1
    }


def print_duplicates(duplicates: dict[str, list[Path]]):
    for paths in duplicates.values():

        print(f"\n{'size':>15} path")
        for p in paths:
            print(f"{p.stat().st_size:>15} {str(p)}")


def move_duplicates(duplicates: dict[str, list[Path]], dest: Path):
    for name, paths in duplicates.items():

        for path in paths[:-1]:
            path.rename(dest / name)


if __name__ == "__main__":
    main()
