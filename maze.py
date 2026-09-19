from typing import Any
from templates import TEMPLATES


class Maze:
    """
    Represents the maze structure and
    encapsulates bitwise state manipulation.
    """

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    IN_MAZE = 16
    SOLID = 32
    VISITED = 64

    ALL_WALLS_MASK = NORTH | EAST | SOUTH | WEST

    DIR_MAP = {
        "N": (0, -1, NORTH, SOUTH),
        "S": (0, 1, SOUTH, NORTH),
        "E": (1, 0, EAST, WEST),
        "W": (-1, 0, WEST, EAST),
    }

    def __init__(
            self,
            settings: dict[str, Any],
    ) -> None:
        self.width: int = settings["WIDTH"]
        self.height: int = settings["HEIGHT"]
        self.entry: tuple[int, int] = settings["ENTRY"]
        self.exit: tuple[int, int] = settings["EXIT"]

        self.matrix: list[list[int]] = self._build_initial_matrix()
        self.has_42: bool = False
        self.easter_egg: bool = False
        self._apply_templates()

    def _build_initial_matrix(self) -> list[list[int]]:
        matrix = []

        for _ in range(self.height):
            row = []
            for _ in range(self.width):
                row.append(self.ALL_WALLS_MASK)
            matrix.append(row)

        return matrix

    def in_grid(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def in_maze(self, x: int, y: int) -> bool:
        return bool(self.matrix[y][x] & self.IN_MAZE)

    def mark_in_maze(self, x: int, y: int) -> None:
        self.matrix[y][x] |= self.IN_MAZE

    def is_solid(self, x: int, y: int) -> bool:
        return bool(self.matrix[y][x] & self.SOLID)

    def mark_solid(self, x: int, y: int) -> None:
        self.matrix[y][x] |= self.SOLID

    def is_visited(self, x: int, y: int) -> bool:
        return bool(self.matrix[y][x] & self.VISITED)

    def mark_visited(self, x: int, y: int) -> None:
        self.matrix[y][x] |= self.VISITED

    def clear_visited(self, x: int, y: int) -> None:
        self.matrix[y][x] &= ~self.VISITED

    def get_wall_mask(self, x: int, y: int) -> int:
        return self.matrix[y][x] & self.ALL_WALLS_MASK

    def has_wall(self, x: int, y: int, wall_bit: int) -> bool:
        return bool(self.matrix[y][x] & wall_bit)

    def _break_partition(self, x: int, y: int, wall_bit: int) -> None:
        self.matrix[y][x] &= ~wall_bit

    def break_wall(
        self,
        x: int,
        y: int,
        bit: int,
        opp_bit: int,
        next_x: int | None = None,
        next_y: int | None = None
    ) -> None:
        self._break_partition(x, y, bit)

        if (
            next_x is not None
            and next_y is not None
            and self.in_grid(next_x, next_y)
        ):
            self._break_partition(next_x, next_y, opp_bit)

    def can_stamp_symbol(self, symbol: list[list[int]]) -> bool:
        if not symbol or not symbol[0]:
            return False

        symbol_width = len(symbol[0])
        symbol_height = len(symbol)

        margin = 2
        required_width = symbol_width + margin
        required_height = symbol_height + margin

        return self.width >= required_width and self.height >= required_height

    def _get_center(self, symbol: list[list[int]]) -> tuple[int, int]:
        symbol_height = len(symbol)
        symbol_width = len(symbol[0])

        start_x = (self.width - symbol_width) // 2
        start_y = (self.height - symbol_height) // 2
        return start_x, start_y

    def _get_bottom_left(self, symbol: list[list[int]]) -> tuple[int, int]:
        symbol_height = len(symbol)
        start_x = 1
        start_y = self.height - symbol_height - 1
        return start_x, start_y

    def _get_bottom_right(self, symbol: list[list[int]]) -> tuple[int, int]:
        symbol_height = len(symbol)
        symbol_width = len(symbol[0])
        start_x = self.width - symbol_width - 1
        start_y = self.height - symbol_height - 1
        return start_x, start_y

    def _get_position_coords(
        self, symbol: list[list[int]], position: str
    ) -> tuple[int, int]:
        if position == "bottom_left":
            return self._get_bottom_left(symbol)
        if position == "bottom_right":
            return self._get_bottom_right(symbol)
        return self._get_center(symbol)

    def _apply_templates(self) -> None:
        symbol_42 = TEMPLATES.get("42_symbol")
        if symbol_42 and self.can_stamp_symbol(symbol_42):
            self.embed_symbol(symbol_42, position="center")
            self.has_42 = True

        if self.width >= 170 and self.height >= 30:
            jaime_user = TEMPLATES.get("jaime_user")
            ruben_user = TEMPLATES.get("ruben_user")
            self.easter_egg = True

            if jaime_user and self.can_stamp_symbol(jaime_user):
                self.embed_symbol(jaime_user, position="bottom_left")

            if ruben_user and self.can_stamp_symbol(ruben_user):
                self.embed_symbol(ruben_user, position="bottom_right")

    def embed_symbol(
        self, symbol: list[list[int]], position: str = "center"
    ) -> None:
        """Stamps a symbol matrix by activating the SOLID flag (32)."""
        symbol_height = len(symbol)
        symbol_width = len(symbol[0])
        start_x, start_y = self._get_position_coords(symbol, position)

        for symbol_y in range(symbol_height):
            for symbol_x in range(symbol_width):
                if symbol[symbol_y][symbol_x] == 1:
                    target_x = start_x + symbol_x
                    target_y = start_y + symbol_y

                    if (target_x, target_y) in (self.entry, self.exit):
                        raise ValueError(
                            "The ENTRY or EXIT overlaps "
                            "with the embedded symbol."
                        )

                    self.mark_solid(target_x, target_y)
