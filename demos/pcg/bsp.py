import random
import pyxel
from operator import attrgetter


class Node:
    def __init__(self, x, y, width=0, height=0, left=None, right=None):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.left = left
        self.right = right

        self.room = None

    @property
    def area(self):
        return self.width * self.height

    def is_leaf(self):
        return self.left is None and self.right is None


class Dungeon:
    def __init__(self, width, height, min_split_size=16, min_area=32):
        self.width = width
        self.height = height
        self.min_split_size = min_split_size
        self.min_area = min_area
        self.root = Node(0, 0, width, height)
        self.leaves = [self.root]
        self.corridors = []

    def reset(self):
        self.root = Node(0, 0, width=self.width, height=self.height)
        self.leaves = [self.root]

    def _choose_leaf(self, rng=False):
        candidates = [leaf for leaf in self.leaves if leaf.area >= self.min_area]
        if candidates:
            if rng:
                return random.choice(candidates)
            return max(candidates, key=attrgetter("area"))
        return None

    def _split_leaf(self, leaf):
        can_split_h = leaf.height >= 2 * self.min_split_size
        can_split_v = leaf.width >= 2 * self.min_split_size

        if not (can_split_h or can_split_v):
            return False

        if can_split_h and can_split_v:
            horizontal = leaf.height > leaf.width
        else:
            horizontal = can_split_h

        if horizontal:
            offset = random.randint(
                self.min_split_size, leaf.height - self.min_split_size
            )
            left = Node(leaf.x, leaf.y, leaf.width, offset)
            right = Node(leaf.x, leaf.y + offset, leaf.width, leaf.height - offset)
        else:
            offset = random.randint(
                self.min_split_size, leaf.width - self.min_split_size
            )
            left = Node(leaf.x, leaf.y, offset, leaf.height)
            right = Node(leaf.x + offset, leaf.y, leaf.width - offset, leaf.height)

        if left.area < self.min_area or right.area < self.min_area:
            return False

        leaf.left, leaf.right = left, right
        self.leaves.remove(leaf)
        self.leaves.extend([left, right])
        return True

    def _room_center(self, node):
        if node.is_leaf():
            rx, ry, rw, rh = node.room
            return rx + rw // 2, ry + rh // 2
        if node.left and any(n.room for n in self._iter_leaves(node.left)):
            return self._room_center(node.left)
        return node._room_center(node.right)

    def _iter_leaves(self, start):
        stack = [start]

        while stack:
            n = stack.pop()
            if n.is_leaf():
                yield n
            else:
                stack.append(n.left)
                stack.append(n.right)

    def carve_rooms(self, min_room_size=8, room_margin=2):
        for leaf in self.leaves:
            max_width = leaf.width - (2 * room_margin)
            max_height = leaf.height - (2 * room_margin)

            if (max_width < min_room_size) or (max_height < min_room_size):
                continue

            r_width = random.randint(min_room_size, max_width)
            r_height = random.randint(min_room_size, max_height)

            r_x = leaf.x + random.randint(
                room_margin, leaf.width - room_margin - r_width
            )
            r_y = leaf.y + random.randint(
                room_margin, leaf.height - room_margin - r_height
            )

            leaf.room = (r_x, r_y, r_width, r_height)

    def carve_corridors(self):
        self.corridors.clear()

        def _connect(node):
            if not node.left or not node.right:
                return
            x1, y1 = self._room_center(node.left)
            x2, y2 = self._room_center(node.right)

            self.corridors.append((x1, y1, x2, y1))
            self.corridors.append((x2, y1, x2, y2))

            _connect(node.left)
            _connect(node.right)

        _connect(self.root)

    def generate(self, n_iter=5):
        for _ in range(n_iter):
            leaf = self._choose_leaf()
            if leaf is None:
                break
            if not self._split_leaf(leaf):
                self.leaves.remove(leaf)


class App:
    def __init__(self, width=128, height=128, fps=30):
        pyxel.init(width, height, fps=fps)
        self.dungeon = Dungeon(width, height)
        self._regen()
        pyxel.run(self.update, self.draw)

    def _regen(self) -> None:
        self.dungeon.reset()
        self.dungeon.generate(n_iter=8)
        self.dungeon.carve_rooms(min_room_size=12, room_margin=2)
        self.dungeon.carve_corridors()

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self._regen()

    def draw(self):
        pyxel.cls(1)
        pyxel.rectb(
            self.dungeon.root.x,
            self.dungeon.root.y,
            self.dungeon.root.width,
            self.dungeon.root.height,
            9,
        )
        stack = [self.dungeon.root]
        while stack:
            node = stack.pop()
            if node.left and node.right:
                # if node.left.width < node.width:
                #     x = node.x + node.left.width
                #     pyxel.line(x, node.y, x, node.y + node.height, 9)
                # else:
                #     y = node.y + node.left.height
                #     pyxel.line(node.x, y, node.x + node.width, y, 9)

                # recurse
                stack.append(node.left)
                stack.append(node.right)

        for leaf in self.dungeon.leaves:
            pyxel.rect(*leaf.room, 9)

        for x1, y1, x2, y2 in self.dungeon.corridors:
            pyxel.line(x1, y1, x2, y2, 9)


if __name__ == "__main__":
    App()
