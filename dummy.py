from pathlib import Path
import random


def generate_dummy_data(dir: str, n_files=1000):
    path = Path(dir)
    path.mkdir()

    dir1 = path / "dir1"
    dir2 = path / "dir2"

    dir1.mkdir()
    dir2.mkdir()

    for n in range(n_files):
        c1 = "A" * random.randint(100, 1000)
        c2 = "B" * random.randint(100, 1000)

        (dir1 / f"{n}.txt").write_text(c1)

        if random.randint(0, 1):
            (dir2 / f"{n}.txt").write_text(c2)


if __name__ == "__main__":
    generate_dummy_data("data")
