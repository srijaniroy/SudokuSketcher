import pygame
import sys
from copy import deepcopy

class SudokuBoard:
    def __init__(self):
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.subgrids = [Subgrid() for _ in range(9)]
        self.lines = [GridLine() for _ in range(18)]

        for row in range(9):
            for col in range(9):
                subgrid_index = (col // 3) + 3 * (row // 3)
                vertical_line_index = col
                horizontal_line_index = row + 9
                new_cell = Cell(self.subgrids[subgrid_index], self.lines[vertical_line_index],
                                self.lines[horizontal_line_index], (row, col))
                self.cells[row][col] = new_cell
                self.subgrids[subgrid_index].cells.append(new_cell)
                self.lines[vertical_line_index].cells.append(new_cell)
                self.lines[horizontal_line_index].cells.append(new_cell)

    def is_valid(self, number, position, grid):
        cell = self.cells[position[0]][position[1]]
        return cell.is_valid(number, grid)

    def solve(self, grid):
        global is_stopped
        global grid_to_display
        if is_stopped:
            return None
        grid_to_display = grid
        handle_input()
        pygame.time.wait(wait_time)
        render_board()

        first_empty_cell = self.find_empty_cell(grid)

        if first_empty_cell is None:
            return grid

        for num in range(1, 10):
            if self.is_valid(num, first_empty_cell, grid):
                new_grid = deepcopy(grid)
                new_grid[first_empty_cell[0]][first_empty_cell[1]] = num
                highlight_cell((125, 125, 125), first_empty_cell)
                result = self.solve(new_grid)
                if result:
                    return result

        return None

    def find_empty_cell(self, grid):
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    return (i, j)
        return None


class Subgrid:
    def __init__(self):
        self.cells = []


class Cell:
    def __init__(self, subgrid, vertical_line, horizontal_line, position):
        self.subgrid = subgrid
        self.vertical_line = vertical_line
        self.horizontal_line = horizontal_line
        self.position = position

    def is_valid(self, number, grid):
        for neighbor in self.subgrid.cells:
            if number == grid[neighbor.position[0]][neighbor.position[1]]:
                return False
        for neighbor in self.vertical_line.cells:
            if number == grid[neighbor.position[0]][neighbor.position[1]]:
                return False
        for neighbor in self.horizontal_line.cells:
            if number == grid[neighbor.position[0]][neighbor.position[1]]:
                return False
        return True


class GridLine:
    def __init__(self):
        self.cells = []


def handle_input():
    global white_color
    global black_color
    global grid_to_display
    global selected_cell
    global highlight
    global current_values
    global sudoku_board
    global is_stopped

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                white_color, black_color = black_color, white_color
            if event.key == pygame.K_r:
                current_values = [[0 for _ in range(9)] for _ in range(9)]
                grid_to_display = current_values
                is_stopped = True
            if event.key == pygame.K_SPACE:
                is_stopped = False
                sudoku_board.solve(current_values)
                highlight = None

            for number in range(1, 10):
                if event.key == getattr(pygame, f"K_{number}") and selected_cell != (-1, -1):
                    if sudoku_board.is_valid(number, selected_cell, current_values):
                        current_values[selected_cell[0]][selected_cell[1]] = number
                        grid_to_display = current_values
                        selected_cell = (-1, -1)
                        highlight = None
                    else:
                        flash_cell(selected_cell)

        if event.type == pygame.MOUSEBUTTONUP:
            is_stopped = True
            grid_to_display = current_values
            selected_cell = get_cell_coordinates(event.pos)
            highlight_cell(green_color, selected_cell)


def highlight_cell(color, cell):
    global offset_height
    global offset_width
    global highlight
    global highlight_color

    cell_size = int(width / 9)
    highlight = pygame.Rect(offset_width + cell[1] * cell_size, offset_height + cell[0] * cell_size, cell_size, cell_size)
    highlight_color = color


def flash_cell(cell_position):
    for _ in range(5):
        highlight_cell(red_color, cell_position)
        render_board()
        pygame.time.wait(10)
        highlight_cell(white_color, cell_position)
        render_board()
        pygame.time.wait(10)
    highlight_cell(green_color, cell_position)
    render_board()


def get_cell_coordinates(pos):
    global offset_height
    global offset_width
    cell_size = int(width / 9)

    x = int((pos[1] - offset_width) / cell_size)
    y = int((pos[0] - offset_height) / cell_size)

    return x, y


def render_board():
    global offset_width
    global offset_height

    screen.fill(white_color)

    max_width = int(width / 9) * 9
    max_height = int(height / 9) * 9
    offset_width = int((width - max_width) / 2)
    offset_height = int((height - max_height) / 2)

    if highlight:
        pygame.draw.rect(screen, highlight_color, highlight)

    for i in range(0, 10):
        intensity = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, black_color, (offset_width + int(width / 9) * i, offset_height), (offset_width + int(width / 9) * i, offset_height + max_height), intensity)
        pygame.draw.line(screen, black_color, (offset_width, offset_height + int(height / 9) * i), (offset_width + max_width, offset_height + int(height / 9) * i), intensity)

    font = pygame.font.Font("Quino.otf", int(0.1 * height))

    for i in range(9):
        for j in range(9):
            char_to_display = "" if str(grid_to_display[i][j]) == "0" else str(grid_to_display[i][j])
            label = font.render(char_to_display, 1, black_color)
            screen.blit(label, get_cell_screen_coordinates((i, j)))

    pygame.display.flip()


def get_cell_screen_coordinates(cell_position):
    global offset_height
    global offset_width
    cell_size = int(width / 9)

    x = offset_height + cell_size * cell_position[1] + int(cell_size / 4)
    y = offset_width + cell_size * cell_position[0] + int(cell_size / 4)

    return x, y


pygame.init()

program_icon = pygame.image.load('icon1.png')
pygame.display.set_icon(program_icon)

with open("settings.txt") as settings_file:
    for line in settings_file:
        parts = line.split(" ")
        if parts[0] == "sleepTimeBetweenMoves":
            wait_time = int(parts[2])
        if parts[0] == "resolution":
            size = width, height = int(parts[2]), int(parts[2])

white_color = (255, 255, 255)
black_color = (0, 0, 0)
red_color = (255, 0, 0)
green_color = (0, 255, 0)
highlight = None
is_stopped = False

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Sudoku Solver by Srijani Roy")

sudoku_board = SudokuBoard()
current_values = [[0 for _ in range(9)] for _ in range(9)]
grid_to_display = current_values

while True:
    handle_input()
    render_board()
