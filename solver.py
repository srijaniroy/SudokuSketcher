import pygame
import sys
from copy import deepcopy

class SudokuGrid:
    def __init__(self):
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.blocks = [Block() for _ in range(9)]
        self.lines = [Line() for _ in range(18)]

        for row in range(9):
            for col in range(9):
                blockIndex = int(col / 3) + 3 * int(row / 3)
                verticalLineIndex = col
                horizontalLineIndex = row + 9
                newCell = Cell(self.blocks[blockIndex], self.lines[verticalLineIndex],
                               self.lines[horizontalLineIndex], (row, col))
                self.cells[row][col] = newCell
                self.blocks[blockIndex].cells.append(newCell)
                self.lines[verticalLineIndex].cells.append(newCell)
                self.lines[horizontalLineIndex].cells.append(newCell)

    def is_cell_valid(self, number, position, grid):
        cell = self.cells[position[0]][position[1]]
        return cell.is_valid(number, grid)

    def solve_sudoku(self, grid):
        global game_stopped
        global grid_to_display
        if game_stopped:
            return None
        grid_to_display = grid
        process_input()
        pygame.time.wait(wait_duration)
        render_grid()

        first_empty_cell = (-1, -1)

        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    first_empty_cell = (i, j)
                    break
            if first_empty_cell[0] != -1:
                break

        if first_empty_cell[0] == -1:
            return grid

        for number_to_try in range(1, 10):
            if self.is_cell_valid(number_to_try, first_empty_cell, grid):
                new_grid = deepcopy(grid)
                new_grid[first_empty_cell[0]][first_empty_cell[1]] = number_to_try
                highlight_cell((125, 125, 125), first_empty_cell)
                result = self.solve_sudoku(new_grid)
                if result:
                    return result

        return None

class Block:
    def __init__(self):
        self.cells = []

class Cell:
    def __init__(self, block, vertical_line, horizontal_line, position):
        self.block = block
        self.vertical_line = vertical_line
        self.horizontal_line = horizontal_line
        self.position = position

    def is_valid(self, number, grid):
        for neighbor_cell in self.block.cells:
            if number == grid[neighbor_cell.position[0]][neighbor_cell.position[1]]:
                return False
        for neighbor_cell in self.vertical_line.cells:
            if number == grid[neighbor_cell.position[0]][neighbor_cell.position[1]]:
                return False
        for neighbor_cell in self.horizontal_line.cells:
            if number == grid[neighbor_cell.position[0]][neighbor_cell.position[1]]:
                return False
        return True

class Line:
    def __init__(self):
        self.cells = []

def process_input():
    global light_color
    global dark_color
    global grid_to_display
    global current_selection
    global highlight
    global sudoku_values
    global sudoku_grid
    global game_stopped

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                light_color, dark_color = dark_color, light_color
            if event.key == pygame.K_r:
                sudoku_values = [[0 for _ in range(9)] for _ in range(9)]
                grid_to_display = sudoku_values
                game_stopped = True
            if event.key == pygame.K_SPACE:
                game_stopped = False
                sudoku_grid.solve_sudoku(sudoku_values)
                highlight = None

            for number in range(1, 10):
                if event.key == getattr(pygame, f"K_{number}") and current_selection != (-1, -1):
                    if sudoku_grid.is_cell_valid(number, current_selection, sudoku_values):
                        sudoku_values[current_selection[0]][current_selection[1]] = number
                        grid_to_display = sudoku_values
                        current_selection = (-1, -1)
                        highlight = None
                    else:
                        flash_cell(current_selection)

        if event.type == pygame.MOUSEBUTTONUP:
            game_stopped = True
            grid_to_display = sudoku_values
            current_selection = get_cell_coordinates(event.pos)
            highlight_cell(green_color, current_selection)

def highlight_cell(color, cell):
    global offset_height
    global offset_width
    global highlight
    global highlight_color

    cell_size = int(width / 9)

    highlight = pygame.Rect(offset_width + cell[1] * cell_size, offset_height + cell[0] * cell_size, cell_size, cell_size)
    highlight_color = color

def flash_cell(cell_number):
    for _ in range(5):
        highlight_cell(red_color, cell_number)
        render_grid()
        pygame.time.wait(10)
        highlight_cell(light_color, cell_number)
        render_grid()
        pygame.time.wait(10)
    highlight_cell(green_color, cell_number)
    render_grid()

def get_cell_coordinates(pos):
    global offset_height
    global offset_width
    cell_size = int(width / 9)

    x = int((pos[1] - offset_width) / cell_size)
    y = int((pos[0] - offset_height) / cell_size)

    return x, y

def get_screen_coordinates_for_cell(cell_position):
    global offset_height
    global offset_width
    cell_size = int(width / 9)

    x = offset_height + cell_size * cell_position[1] + int(cell_size / 4)
    y = offset_width + cell_size * cell_position[0] + int(cell_size / 4)

    return x, y

def render_grid():
    global offset_width
    global offset_height

    screen.fill(light_color)

    max_width = int(width / 9) * 9
    max_height = int(height / 9) * 9
    offset_width = int((width - max_width) / 2)
    offset_height = int((height - max_height) / 2)

    if highlight:
        pygame.draw.rect(screen, highlight_color, highlight)

    for i in range(0, 10):
        intensity = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, dark_color, (offset_width + int(width / 9) * i, offset_height), (offset_width + int(width / 9) * i, offset_height + max_height), intensity)
        pygame.draw.line(screen, dark_color, (offset_width, offset_height + int(height / 9) * i), (offset_width + max_width, offset_height + int(height / 9) * i), intensity)

    font = pygame.font.Font("Quino.otf", int(0.1 * height))

    for i in range(9):
        for j in range(9):
            char_to_display = "" if str(grid_to_display[i][j]) == "0" else str(grid_to_display[i][j])
            label = font.render(char_to_display, 1, dark_color)
            screen.blit(label, get_screen_coordinates_for_cell((i, j)))

    pygame.display.flip()

pygame.init()

program_icon = pygame.image.load('icon1.png')

pygame.display.set_icon(program_icon)

with open("settings.txt") as settings_file:
    for line in settings_file:
        parts = line.split(" ")
        if parts[0] == "sleepTimeBetweenMoves":
            wait_duration = int(parts[2])
        if parts[0] == "resolution":
            size = width, height = int(parts[2]), int(parts[2])

light_color = (255, 255, 255)
dark_color = (0, 0, 0)
red_color = (255, 0, 0)
green_color = (0, 255, 0)
highlight = None
game_stopped = False

screen = pygame.display.set_mode(size)
pygame.display.set_caption("Sudoku Solver by Tymscar")

sudoku_grid = SudokuGrid()
sudoku_values = [[0 for _ in range(9)] for _ in range(9)]
grid_to_display = sudoku_values

while True:
    process_input()
    render_grid()
