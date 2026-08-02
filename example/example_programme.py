from pprint import pprint as pprint
from os import system as cmd
from time import sleep as wait
from random import randint as randomint
from random import choice as choose
import sys

if sys.platform == "win32":
    import msvcrt

    def get_char(prompt=""):
        if prompt:
            print(prompt, end="", flush=True)
        char = msvcrt.getch()
        try:
            return char.decode("utf-8").lower()
        except UnicodeDecodeError:
            return ""

else:
    import tty
    import termios

    def get_char():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char.lower()

class Feild:
    def __init__(self, x_size, y_size):
        self.feild = []
        self.x = x_size
        self.y = y_size
        for counter in range(self.x):
            self.feild.append([])
            for counter_1 in range(self.y):
                self.feild[counter].append(" ")
        print("board initialized")

    def import_from_maze(self, maze):
        for cell_counter in range(len(maze)):
            for counter in range(len(maze[cell_counter])):
                self.feild[cell_counter][counter] = maze[cell_counter][counter].char

    def render(self):
        wait(0.1)
        cmd("clear")
        print("\033[H", end="", flush=True)

        for obj in list(Gameobj.objlist):
            obj.eff()

        render_grid = []
        for counter in range(self.x):
            render_grid.append([])
            for counter_1 in range(self.y):
                render_grid[counter].append(self.feild[counter][counter_1])

        for obj in Gameobj.objlist:
            x = obj.x
            y = obj.y
            render_grid[x][y] = obj.symbol

        for row in render_grid:
            for char in row:
                print(char, end="")
            print()

    def get_obj_at_coord(self, x, y):
        return self.feild[x][y]

class Gameobj:
    objlist = []

    def __init__(self, x, y, hp, symbol):
        Gameobj.objlist.append(self)
        self.stat_eff = 0
        self.amt = 0
        self.x = x
        self.y = y
        self.hp = hp
        self.symbol = symbol

    def moveto(self, x, y):
        self.x = x
        self.y = y

    def attack(self, to_dmg, dmg):
        to_dmg.stat_eff = 0b00000001
        to_dmg.amt = dmg

    def eff(self):
        if self.amt >= 1 and self.stat_eff == 0b00000001:
            self.hp -= self.amt
            if self.hp <= 0:
                self.kill()
            else:
                self.amt = 0
                self.stat_eff = 0

    def kill(self):
        Gameobj.objlist.remove(self)

class Player(Gameobj):
    def __init__(self, x, y,hp , symbol):
        super().__init__(x, y,hp , symbol)

class Mazewall:
    def __init__(self):
        self.char = "█"

    def __repr__(self):
        return self.char

class Mazecell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = " "

    def __repr__(self):
        return self.char

class Mazegen:
    def __init__(self, x_size, y_size):
        self.x_size = x_size
        self.y_size = y_size

        self.feild = []
        for counter in range(x_size):
            collum = []
            for counter_1 in range(y_size):
                collum.append(Mazewall())
            self.feild.append(collum)

        self.wall_list = []

        start_x = randomint(0, x_size - 1)
        start_y = randomint(0, y_size - 1)
        self.feild[start_x][start_y] = Mazecell(start_x, start_y)

        self.add_neighbors_to_wall_list(start_x, start_y)

        while self.wall_list:
            wallx, wally = choose(self.wall_list)
            self.wall_list.remove((wallx, wally))

            neighbors = self.get_neighbors(wallx, wally)
            visited_count = sum(
                1
                for neighbourx, neighboury in neighbors
                if isinstance(self.feild[neighbourx][neighboury], Mazecell)
            )

            if visited_count == 1:
                self.feild[wallx][wally] = Mazecell(wallx, wally)
                self.add_neighbors_to_wall_list(wallx, wally)

    def export_maze(self):
        return self.feild

    def get_neighbors(self, x, y):
        neighbors = []
        for deltax, deltay in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]:
            neighbourx, neighboury = x + deltax, y + deltay
            if 0 <= neighbourx < self.x_size and 0 <= neighboury < self.y_size:
                neighbors.append((neighbourx, neighboury))
        return neighbors

    def add_neighbors_to_wall_list(self, x, y):
        for neighbourx, neighboury in self.get_neighbors(x, y):
            if (
                isinstance(self.feild[neighbourx][neighboury], Mazewall)
                and (neighbourx, neighboury) not in self.wall_list
            ):
                self.wall_list.append((neighbourx, neighboury))

class Pathfind:
    def __init__(self, start, target, grid):
        self.sx, self.sy = start.x, start.y
        self.tx, self.ty = target.x, target.y

        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

        self.path = self.solve_bfs()

    def solve_bfs(self):
        start_node = (self.sx, self.sy)
        target_node = (self.tx, self.ty)

        if not self._is_valid(self.sx, self.sy) or not self._is_valid(self.tx, self.ty):
            return []

        queue = [start_node]
        head = 0

        visited = {start_node: True}
        parent = {start_node: None}

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while head < len(queue):
            curr_x, curr_y = queue[head]
            head += 1

            if (curr_x, curr_y) == target_node:
                return self._reconstruct_path(parent, target_node)

            for dx, dy in directions:
                nx, ny = curr_x + dx, curr_y + dy
                neighbor = (nx, ny)

                if self._is_valid(nx, ny) and neighbor not in visited:
                    visited[neighbor] = True
                    parent[neighbor] = (curr_x, curr_y)
                    queue.append(neighbor)

        return []

    def _is_valid(self, x, y):
        # Bounds check and wall verification (assuming 0 is open, 1 is wall)
        return 0 <= x < self.rows and 0 <= y < self.cols and self.grid[x][y] == " "

    def _reconstruct_path(self, parent, target_node):
        path = []
        curr = target_node

        while curr is not None:
            path.append(curr)
            curr = parent[curr]

        return path[::-1]

class Game:
    @staticmethod
    def main():
        print("\033[?25l", end="", flush=True)  # steal cursor
        try:
            score = 0
            while True:
                curscore = 600
                Gameobj.objlist.clear()

                maze = Mazegen(
                    maze_dat["x"]["max"] - maze_dat["x"]["min"] + 1,
                    maze_dat["y"]["max"] - maze_dat["y"]["min"] + 1,
                )

                feild = Feild(
                    maze_dat["x"]["max"] - maze_dat["x"]["min"] + 1,
                    maze_dat["y"]["max"] - maze_dat["y"]["min"] + 1,
                )
                feild.import_from_maze(maze.export_maze())

                exit_spawned = False
                valid_spawn = False
                while not valid_spawn:
                    px = randomint(
                        maze_dat["x"]["min"],
                        maze_dat["x"]["max"]
                    )

                    py = randomint(
                        maze_dat["y"]["min"],
                        maze_dat["y"]["max"]
                    )
                    if feild.get_obj_at_coord(px, py) == " ":
                        player = Player(px, py, 1, "@")
                        valid_spawn = True

                enemy_list = []
                enemy_count = randomint(1, 5)

                while enemy_count > 0:
                    x_pos = randomint(
                        maze_dat["x"]["min"],
                        maze_dat["x"]["max"]
                    )

                    y_pos = randomint(
                        maze_dat["y"]["min"],
                        maze_dat["y"]["max"]
                    )
                    if feild.get_obj_at_coord(x_pos, y_pos) == " " and (
                        x_pos,
                        y_pos,
                    ) != (player.x, player.y):
                        enemy_list.append(Gameobj(x_pos, y_pos, 1, "#"))
                        enemy_count -= 1

                feild.render()

                while enemy_list:
                    Game.input(feild, player, score)

                    # do later Pathfind(enemy_list[0], player, maze)

                    for enemy in list(enemy_list):
                        if enemy.x == player.x and enemy.y == player.y:
                            player.attack(enemy, 1)
                            feild.render()
                            score += 10
                            if enemy not in Gameobj.objlist:
                                enemy_list.remove(enemy)
                            break

                    feild.render()
                    curscore -= 1


                while not exit_spawned:
                    x_pos = randomint(
                        maze_dat["x"]["min"],
                        maze_dat["x"]["max"]
                    )

                    y_pos = randomint(
                        maze_dat["y"]["min"],
                        maze_dat["y"]["max"]
                    )
                    if feild.get_obj_at_coord(x_pos, y_pos) == " " and (
                        x_pos,
                        y_pos,
                    ) != (player.x, player.y):
                        exit = Gameobj(x_pos, y_pos, 1, "E")
                        exit_spawned = True

                while len(Gameobj.objlist) > 1:
                    feild.render()
                    Game.input(feild, player, score)

                    if exit.x == player.x and exit.y == player.y:
                        exit.kill()
                        score += curscore
                        print("Next level")
                    curscore -= 1

                feild.render()

                wait(1.5)
        finally:
            print("\033[?25h", end="", flush=True)  # return cursor

    @staticmethod
    def input(feild, player, score):
        print(f"[W]Up [A]Left [S]Down [D]Right [Q]uit Score: {score}", end="", flush=True)
        dir = get_char()
        print(dir)
        if dir == "q":
            raise SystemExit
        target_x, target_y = player.x, player.y
        if dir == "w":
            target_x = max(
                maze_dat["x"]["min"],
                player.x - 1
            )
        elif dir == "s":
            target_x = min(maze_dat["x"]["max"], player.x + 1)
        elif dir == "a":
            target_y = max(maze_dat["y"]["min"], player.y - 1)
        elif dir == "d":
            target_y = min(maze_dat["y"]["max"], player.y + 1)
        if feild.get_obj_at_coord(target_x, target_y) != "█":
            player.moveto(target_x, target_y)

global maze_dat
maze_dat = {"x": {"min": 0, "max": 45},
            "y": {"min": 0, "max": 100}}
Game.main()
