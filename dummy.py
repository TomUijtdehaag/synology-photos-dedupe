from pathlib import Path
import random


def generate_dummy_data(dir: str, n_files=1000, n_dirs=2):
    path = Path(dir)
    path.mkdir()

    dirs = []
    for d in range(n_dirs):
        dirs.append(path / f"dir{d}")

    for d in dirs:
        d.mkdir()

    for n in range(n_files):

        for d in dirs[1:]:
            if random.randint(0, 1):
                c = "A" * random.randint(100, 1000)
                (d / f"{n}.txt").write_text(c)


if __name__ == "__main__":
    generate_dummy_data("data", n_dirs=5)
