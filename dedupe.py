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

    if not args.dry_run:
        dest.mkdir(exist_ok=True)
        move_duplicates(duplicates, dest)


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
    if len(duplicates) == 0:
        print("No duplicates found")
        return

    for name, paths in duplicates.items():
        print()
        print(f"{'size':>15} path")
        for p in paths:
            print(f"{p.stat().st_size:>15} {str(p)}")


def move_duplicates(duplicates: dict[str, list[Path]], dest: Path):
    for name, paths in duplicates.items():

        for path in paths[:-1]:
            path.rename(dest / name)


if __name__ == "__main__":
    main()
