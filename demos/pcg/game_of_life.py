import pyxel
import numpy as np


class Universe:
    def __init__(self, size: int = 64, alive_prob: float = 0.2) -> None:
        self.size = size
        self.alive_prob = alive_prob
        self._grid = self._random_grid()

    def _random_grid(self) -> np.ndarray:
        return np.random.rand(self.size, self.size) < self.alive_prob

    @property
    def grid(self) -> np.ndarray:
        return self._grid

    def reset(self) -> None:
        self._grid = self._random_grid()

    def step(self) -> None:
        neighbors = sum(
            np.roll(np.roll(self._grid, dx, axis=0), dy, axis=1)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
            if not (dx == 0 and dy == 0)
        )
        birth = (neighbors == 3) & ~self._grid
        survive = ((neighbors == 2) | (neighbors == 3)) & self._grid

        self._grid = birth | survive


class App:
    def __init__(
        self, size: int = 64, cell_color: int = 9, bg_color: int = 1, fps: int = 30
    ) -> None:
        self.size = size
        self.cell_color = cell_color
        self.bg_color = bg_color
        self.universe = Universe(size)
        self.running = False

        pyxel.init(self.size, self.size, fps=fps)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_R):
            self.universe.reset()
            self.running = False

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.running = not self.running

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._toggle_cell(pyxel.mouse_x, pyxel.mouse_y)

        if self.running and pyxel.frame_count % 10 == 0:
            self.universe.step()

    def draw(self) -> None:
        pyxel.cls(self.bg_color)
        grid = self.universe.grid
        for x, y in zip(*np.where(grid)):
            pyxel.pset(x, y, self.cell_color)

    def _toggle_cell(self, x: int, y: int) -> None:
        self.universe.grid[x, y] = not self.universe.grid[x, y]


App()
