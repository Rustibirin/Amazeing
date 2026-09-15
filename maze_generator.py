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

    def valid_moves(self, coords: tuple[int, int]) -> list[int]:
        valids = [1, 2, 4, 8]
        if (coords[0] == 0):
            valids.remove(8)
        elif (coords[0] == self.width - 1):
            valids.remove(2)
        if (coords[1] == 0):
            valids.remove(1)
        elif (coords[1] == self.height - 1):
            valids.remove(4)
        return (valids)

    def make_move(self, curr: tuple[int, int],
                  move: int) -> tuple[int, int]:
        if (move == 1):
            return ((curr[0], curr[1] - 1))
        elif (move == 4):
            return ((curr[0], curr[1] + 1))
        elif (move == 2):
            return ((curr[0] + 1, curr[1]))
        else:
            return ((curr[0] - 1, curr[1]))

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

    def gen_perfect(self) -> tuple[list[list[int]], list[tuple[int, int]]]:
        maze = self.gen_base(15)
        width = self.config['WIDTH']
        height = self.config['HEIGHT']
        unvisited = {(x, y)
                     for x in range(width)
                     for y in range(height)
                     }
        entry_x, entry_y = self.config['ENTRY']
        unvisited.discard((entry_x, entry_y))

        while unvisited:
            if (len(unvisited) + 1) == width * height:
                curr = self.config['EXIT']
            else:
                curr = random.choice(list(unvisited))
            path = [curr]
            while curr in unvisited:
                valid_moves = self.valid_moves(curr)
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
                x1, y1 = path[elm]
                x2, y2 = path[elm + 1]
                self.modify_maze(maze, x1, y1, x2, y2)
                unvisited.discard((x1, y1))
            unvisited.discard(path[-1])
        return (maze, solution)

    def generation(self) -> list[tuple[int, int]]:
        "We generate our maze attending to its perfection"
        maze, solution = self.gen_perfect()
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
