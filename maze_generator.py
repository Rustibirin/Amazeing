import random
from typing import Any


class MazeGenerator():
    "The aim of this class is to control the generation of the maze required"
    def __init__(self, config: dict[str, Any]) -> None:
        "We save the config of our actual maze"
        self.config = config
        self.height = self.config['HEIGHT']
        self.width = self.config['WIDTH']

    def gen_base(self, fill: int) -> list[list[int]]:
        maze: list[list[int]] = []
        row: list[int] = []
        for _ in range(self.config['HEIGHT']):
            for _ in range(self.config['WIDTH']):
                row.append(fill)
            maze.append(row)
            row = []
        return (maze)

    def entry_exit_in_protected(self) -> bool:
        width = self.width
        height = self.height
        cx, cy = ((width - 1) // 2, (height - 1) // 2)
        ent = self.config['ENTRY']
        ext = self.config['EXIT']
        for i in range(3):
            if ((cx + 1 + i, cy) == ent or (cx + 1 + i, cy) == ext):
                return (True)
            if ((cx - 1 - i, cy) == ent or (cx - 1 - i, cy) == ext):
                return (True)
            if ((cx + 1, cy + i) == ent or (cx + 1, cy + i) == ext):
                return (True)
            if ((cx - 1, cy + i) == ent or (cx - 1, cy + i) == ext):
                return (True)
            if ((cx + 1 + i, cy + 2) == ent or (cx + 1 + i, cy + 2) == ext):
                return (True)
            if ((cx + 3, cy - i) == ent or (cx + 3, cy - i) == ext):
                return (True)
            if ((cx + 1 + i, cy - 2) == ent or (cx + 1 + i, cy - 2) == ext):
                return (True)
            if ((cx - 3, cy - i) == ent or (cx - 3, cy - i) == ext):
                return (True)
        return (False)

    def valid_moves(self, coords: tuple[int, int],
                    protected: list[list[int]]) -> list[int]:
        valids = [1, 2, 4, 8]
        if (coords[1] == 0):
            valids.remove(8)
        elif (coords[1] == self.width - 1):
            valids.remove(2)
        if (coords[0] == 0):
            valids.remove(1)
        elif (coords[0] == self.height - 1):
            valids.remove(4)
        if ((coords[1] < self.width - 1)
                and protected[coords[0]][coords[1] + 1]):
            valids.remove(2)
        if ((coords[1] > 0)
                and protected[coords[0]][coords[1] - 1]):
            valids.remove(8)
        if ((coords[0] < self.height - 1)
                and protected[coords[0] + 1][coords[1]]):
            valids.remove(4)
        if ((coords[0] > 0)
                and protected[coords[0] - 1][coords[1]]):
            valids.remove(1)
        return (valids)

    def make_move(self, curr: tuple[int, int],
                  move: int) -> tuple[int, int]:
        if (move == 1):
            return ((curr[0] - 1, curr[1]))
        elif (move == 4):
            return ((curr[0] + 1, curr[1]))
        elif (move == 2):
            return ((curr[0], curr[1] + 1))
        else:
            return ((curr[0], curr[1] - 1))

    def modify_maze(self, maze: list[list[int]],
                    x1: int, y1: int,
                    x2: int, y2: int) -> list[list[int]]:
        if (x1 > x2):
            maze[y1][x1] -= 8
            maze[y2][x2] -= 2
        elif (x1 < x2):
            maze[y1][x1] -= 2
            maze[y2][x2] -= 8
        else:
            if (y1 > y2):
                maze[y1][x1] -= 1
                maze[y2][x2] -= 4
            else:
                maze[y1][x1] -= 4
                maze[y2][x2] -= 1
        return (maze)

    def protect_42(self, base: list[list[int]]) -> list[tuple[int, int]]:
        width = self.width
        height = self.height
        index_protected = []
        cx, cy = ((width - 1) // 2, (height - 1) // 2)
        for i in range(3):
            index_protected.append((cy, cx + 1 + i))
            index_protected.append((cy, cx - 1 - i))
            index_protected.append((cy + i, cx + 1))
            index_protected.append((cy + i, cx - 1))
            index_protected.append((cy + 2, cx + 1 + i))
            index_protected.append((cy - i, cx + 3))
            index_protected.append((cy - 2, cx + 1 + i))
            index_protected.append((cy - i, cx - 3))
        return (index_protected)

    def gen_perfect(self, flag_42: bool
                    ) -> tuple[list[list[int]], list[tuple[int, int]]]:
        cells_protected: list[list[int]] = [[0 for _ in range(self.width)
                                             ].copy()
                                            for _ in range(self.height)
                                            ]
        if (flag_42):
            index_protected = self.protect_42(cells_protected)
            for indexes in index_protected:
                cells_protected[indexes[0]][indexes[1]] = 1
        maze = self.gen_base(15)
        width = self.config['WIDTH']
        height = self.config['HEIGHT']
        unvisited = {(y, x)
                     for x in range(width)
                     for y in range(height)
                     }
        entry_x, entry_y = self.config['ENTRY']
        unvisited.discard((entry_y, entry_x))
        candidates = unvisited.copy()
        if (flag_42):
            for indexes in index_protected:
                candidates.discard(indexes)
        while candidates:
            if ((len(unvisited) + 1) == width * height):
                curr = (self.config['EXIT'][1], self.config['EXIT'][0])
            else:
                curr = random.choice(list(candidates))
            path = [curr]
            while curr in unvisited:
                valid_moves = self.valid_moves(curr, cells_protected)
                next_move = random.choice(valid_moves)
                nxt = self.make_move(curr, next_move)
                if (nxt in path):
                    retry = path.index(nxt)
                    path = path[:retry + 1]
                else:
                    path.append(nxt)
                curr = nxt
            if (len(unvisited) + 1) == width * height:
                solution = path.copy()
            for elm in range(len(path) - 1):
                y1, x1 = path[elm]
                y2, x2 = path[elm + 1]
                self.modify_maze(maze, x1, y1, x2, y2)
                unvisited.discard((y1, x1))
            unvisited.discard(path[-1])
            candidates = unvisited.copy()
            if (flag_42):
                for indexes in index_protected:
                    candidates.discard(indexes)
        return (maze, solution)

    def generation(self) -> list[tuple[int, int]]:
        "We generate our maze attending to its perfection"
        if (self.width >= 9 and self.height >= 7):
            if not (self.entry_exit_in_protected()):
                maze, solution = self.gen_perfect(True)
            else:
                maze, solution = self.gen_perfect(False)
        else:
            maze, solution = self.gen_perfect(False)
        text = ""
        HEX_DICT: dict[int, str] = {
            0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7',
            8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c', 13: 'd',
            14: 'e', 15: 'f'
        }
        for row in maze:
            for elm in row:
                text += f"{HEX_DICT[elm]}"
            text += "\n"
        fich = open(self.config['OUTPUT_FILE'], "w")
        fich.write(text[:-1])
        return (solution)
