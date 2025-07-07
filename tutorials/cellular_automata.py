import pyxel
import numpy as np


class Cave:
    def __init__(self, size: int, fill_prob=0.6) -> None:
        self.size = size
        self.fill_prob = fill_prob
        self._grid = self._random_grid()
        self.generate()

    def _random_grid(self) -> np.ndarray:
        return np.random.rand(self.size, self.size) < self.fill_prob

    @property
    def grid(self) -> np.ndarray:
        return self._grid

    def reset(self) -> None:
        self._grid = self._random_grid()

    def get_neighbors(self, neighbor_range=1):
        neighbors = sum(
            np.roll(np.roll(self._grid, dx, axis=0), dy, axis=1)
            for dx in list(range(-neighbor_range, neighbor_range + 1, 1))
            for dy in list(range(-neighbor_range, neighbor_range + 1, 1))
            if not (dx == 0 and dy == 0)
        )
        return neighbors

    def generate(self) -> None:
        for _ in range(4):
            neighbors_1 = self.get_neighbors(1)
            neighbors_2 = self.get_neighbors(2)

            self._grid = (neighbors_1 >= 5) | (neighbors_2 <= 1)
        for _ in range(3):
            neighbors_1 = self.get_neighbors(1)
            self._grid = neighbors_1 >= 5


class App:
    def __init__(
        self, size: int = 64, cell_color: int = 9, bg_color: int = 1, fps: int = 30
    ) -> None:
        self.size = size
        self.cell_color = cell_color
        self.bg_color = bg_color
        self.cave = Cave(size)

        pyxel.init(self.size, self.size, fps=fps)
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_R):
            self.cave.reset()
            self.cave.generate()

    def draw(self) -> None:
        pyxel.cls(self.bg_color)
        grid = self.cave.grid
        for x, y in zip(*np.where(grid)):
            pyxel.pset(x, y, self.cell_color)


App()
