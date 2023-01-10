from pathlib import Path
import shutil
import random

from typing import List


def generate_dummy_data(dir: str, n_files=1000, n_dirs=2):
    path = Path(dir)
    path.mkdir()

    dirs: List[Path] = []
    for d in range(n_dirs):
        dirs.append(path / f"dir{d}")

    for d in dirs:
        d.mkdir()

    for n in range(n_files):
        c = "A" * random.randint(1, 100)
        file: Path = dirs[0] / f"{n}.txt"
        file.write_text(c)

    for file in dirs[0].glob("*"):
        for d in dirs[1:]:
            if random.randint(0, 1):
                shutil.copy(file, d / file.name)


if __name__ == "__main__":
    generate_dummy_data("data", n_dirs=5)
