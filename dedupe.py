import argparse
import re
from pathlib import Path
import time
from typing import Dict, List, Tuple

from PIL import Image
from pillow_heif import register_heif_opener
from tqdm import tqdm

register_heif_opener()


def main():
    parser = argparse.ArgumentParser(prog="Synology Photos Dedupe")

    parser.add_argument(
        "--dirs", nargs="+", required=True, help="Directories to scan for duplicates"
    )
    parser.add_argument(
        "--filters",
        nargs="+",
        help="Skip paths that contain these (sub-)folders or filenames",
    )
    parser.add_argument(
        "--dest", required=True, help="Destination directory to move duplicates to"
    )
    parser.add_argument("-e", "--ext", nargs="+", help="File extensions to consider")
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Only scan and show duplicate files",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print table of duplicate files"
    )

    args = parser.parse_args()

    # source dirs
    dirs = [Path(d) for d in args.dirs]

    # destination dir
    dest = Path(args.dest)

    # extensions
    if args.ext:
        extensions = args.ext
    else:
        extensions = ["jpg", "png", "jpeg", "gif", "mp4", "webp", "heic", "raf"]
    extensions = list(map(str.lower, extensions)) + list(map(str.upper, extensions))

    duplicates = find_duplicate_names(dirs, extensions, args.filters)
    duplicates = add_date(duplicates)

    if args.verbose or args.dry_run:
        print_duplicates(duplicates)

    max_dupes = stats(duplicates)

    if not args.dry_run and input("Continue? y/[n]: ") == "y":
        dest.mkdir(exist_ok=True)
        move_duplicates(duplicates, dest, max_dupes)

    else:
        print("No files moved.")


def stats(duplicates):
    total_dupes = 0
    max_dupes = 0
    for files in duplicates.values():
        total_dupes += len(files)

        if len(files) > max_dupes:
            max_dupes = len(files)

    print(
        f"Found dupes of {len(duplicates)} files. Total: {total_dupes}. Max: {max_dupes}"
    )

    return max_dupes


def find_duplicate_names(
    dirs: List[Path], extensions: List[str], filters: List[str]
) -> Dict[str, List[Path]]:
    filenames = {}
    for dir in dirs:
        for ext in extensions:
            for path in dir.glob(f"**/*.{ext}"):
                if not path.is_file():
                    continue

                if filters is not None and any([f in path.parts for f in filters]):
                    continue

                key = re.sub(r"\([0-9]\)", "", path.name)

                paths = filenames.get(key, [])
                paths.append(path)
                filenames[key] = paths

    return {
        name: sorted(paths, key=lambda x: x.stat().st_size)
        for name, paths in filenames.items()
        if len(paths) > 1
    }


def add_date(duplicates: Dict[str, List[Path]]) -> Dict[Tuple[str, str], List[Path]]:
    new_duplicates = {}
    for name, paths in tqdm(duplicates.items()):
        for path in paths:
            try:
                img = Image.open(path)

                # DateTimeOriginal
                exif = img.getexif()

                if exif is None:
                    continue

                # timestamp = exif.get(36867)
                timestamp = exif.get(306)

                if timestamp:
                    # use only date
                    timestamp = timestamp.split()[0]

                # fallback to file date
                else:
                    timestamp = time.localtime(path.stat().st_mtime)
                    timestamp = time.strftime("%Y:%m:%d")

                files = new_duplicates.get((name, timestamp), [])
                files.append(path)
                new_duplicates[(name, timestamp)] = files

            except Exception:
                print("Failed to read:", path)

    return {
        name: sorted(paths, key=lambda x: x.stat().st_size)
        for name, paths in new_duplicates.items()
        if len(paths) > 1
    }


def print_duplicates(duplicates: Dict[str, List[Path]]):
    print("|" + "-" * 123 + "|")
    print(f"|{'size':>15} | {'path':<105}|")

    for paths in duplicates.values():
        print("|" + "-" * 123 + "|")
        for p in paths:
            print(f"|{p.stat().st_size:>15} | {str(p):<105}|")
    print("|" + "-" * 123 + "|")


def move_duplicates(
    duplicates: Dict[Tuple[str, str], List[Path]], dest: Path, max_dupes: int
):

    for i in range(max_dupes - 1):
        (dest / str(i)).mkdir()

    move_count = 0
    for paths in duplicates.values():

        for i, path in enumerate(paths[:-1]):
            path.rename(dest / str(i) / path.name)
            move_count += 1

    print(f"Moved {move_count} files to {dest}.")


if __name__ == "__main__":
    main()
