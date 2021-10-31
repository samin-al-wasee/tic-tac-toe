import math
import numpy as np
import pygame
import random
import sys

global current_state


def reset_state():
    global current_state
    current_state = np.zeros((3, 3), dtype="int8")
    print("Grid Reset!")


def find_depth(state):
    return len(list(filter(lambda is_empty: is_empty, state.flatten() == 0)))


def check_win_condition(state):
    check_rows = np.sum(state, axis=1)
    check_columns = np.sum(state, axis=0)
    check_primary_diagonal = np.trace(state)
    check_secondary_diagonal = np.trace(state[::-1])
    if np.any(check_columns == 3) or np.any(check_rows == 3) \
            or check_primary_diagonal == 3 or check_secondary_diagonal == 3:
        return True, +3
    elif np.any(check_columns == -3) or np.any(check_rows == -3) \
            or check_primary_diagonal == -3 or check_secondary_diagonal == -3:
        return True, -3
    return False, 0


def evaluate_state(state):
    empty_cells = find_depth(state)
    if check_win_condition(state)[0]:
        if check_win_condition(state)[1] > 0:
            return 10 - 9 + empty_cells
        return -10 + 9 - empty_cells
    if empty_cells > 0:
        return None
    return 0


def get_possible_states(state, value):
    temp_all_possible_states = []
    is_empty_cell = state == 0
    for row in range(len(is_empty_cell)):
        for column in range(len(is_empty_cell[row])):
            if is_empty_cell[row][column]:
                temp_all_possible_states.append(state.copy())
                temp_all_possible_states[-1][row][column] = value
    return temp_all_possible_states


def generate_states(state, is_maximizing):
    if is_maximizing:
        return get_possible_states(state, 1)
    return get_possible_states(state, -1)


def get_best_state(state, depth, is_maximizing, alpha, beta):
    best_possible_value = -math.inf
    best_possible_state = None
    worst_possible_value = math.inf
    worst_possible_state = None
    current_value = evaluate_state(state)
    if current_value is not None:
        return current_value, state
    if is_maximizing:
        for state in generate_states(state, is_maximizing):
            current_value = get_best_state(state, depth - 1, not is_maximizing, alpha, beta)[0]
            if max(best_possible_value, current_value) == current_value:
                best_possible_value = current_value
                best_possible_state = state
            alpha = max(alpha, best_possible_value)
            if alpha > beta:
                break
        return best_possible_value, best_possible_state
    for state in generate_states(state, is_maximizing):
        current_value = get_best_state(state, depth - 1, not is_maximizing, alpha, beta)[0]
        if min(worst_possible_value, current_value) == current_value:
            worst_possible_value = current_value
            worst_possible_state = state
        beta = min(beta, worst_possible_value)
        if alpha > beta:
            break
    return worst_possible_value, worst_possible_state


def get_move_index(state, desired_state):
    is_empty_cell_before = state == 0
    is_empty_cell_after = desired_state == 0
    move = np.where(np.bitwise_xor(is_empty_cell_before, is_empty_cell_after))
    move_row = move[0][0]
    move_column = move[1][0]
    return move_row, move_column


def generate_random_color_code(start, end):
    return random.randint(start, end)


def create_game_window():
    window_size = [1250, 650]
    bg_color = [generate_random_color_code(150, 255), generate_random_color_code(150, 255),
                generate_random_color_code(150, 255)]
    window = pygame.display.set_mode(window_size)
    window.fill(bg_color)
    return window


def draw_line_animate(window, begin, end, color, width):
    if begin[0] == end[0]:
        for point in range(begin[1], end[1]):
            pygame.draw.line(window, color, (begin[0], point), (end[0], point + 1), width)
            pygame.display.update()
    for point in range(begin[0], end[0]):
        pygame.draw.line(window, color, (point, begin[1]), (point + 1, end[1]), width)
        pygame.display.update()


def draw_grid(window):
    line_color = [generate_random_color_code(0, 150), generate_random_color_code(0, 150),
                  generate_random_color_code(0, 150)]
    line_width = 5
    draw_line_animate(window, [525, 25], [525, 625], line_color, line_width)
    draw_line_animate(window, [725, 25], [725, 625], line_color, line_width)
    draw_line_animate(window, [325, 225], [925, 225], line_color, line_width)
    draw_line_animate(window, [325, 425], [925, 425], line_color, line_width)


def reset_game_window():
    pygame.time.wait(500)
    game_window.fill((generate_random_color_code(150, 255), generate_random_color_code(150, 255),
                      generate_random_color_code(150, 255)))
    pygame.display.update()
    draw_grid(game_window)
    reset_state()


def check_click_validity(mouse_click_offset):
    return 325 <= mouse_click_offset[0] <= 925


def decide_cell(mouse_click_offset):
    row = (mouse_click_offset[0] - 325) // 200
    column = (mouse_click_offset[1] - 25) // 200
    return [row, column]


def calculate_x_position(cell):
    return [375 + cell[0] * 200, 75 + cell[1] * 200], [475 + cell[0] * 200, 175 + cell[1] * 200], \
           [475 + cell[0] * 200, 75 + cell[1] * 200], [375 + cell[0] * 200, 175 + cell[1] * 200]


def put_x(cell):
    x_color = [generate_random_color_code(100, 150), generate_random_color_code(100, 150),
               generate_random_color_code(100, 150)]
    x_width = 10
    left_diagonal_start, left_diagonal_end, right_diagonal_start, right_diagonal_end \
        = calculate_x_position(cell)
    pygame.draw.line(game_window, x_color, left_diagonal_start, left_diagonal_end, x_width)
    pygame.display.update()
    pygame.time.wait(100)
    pygame.draw.line(game_window, x_color, right_diagonal_start, right_diagonal_end, x_width)
    pygame.display.update()


def put_o(cell):
    o_color = [generate_random_color_code(50, 100), generate_random_color_code(50, 100),
               generate_random_color_code(50, 100)]
    o_width = 5
    o_center = [425 + cell[0] * 200, 125 + cell[1] * 200]
    o_radius = 65
    pygame.draw.circle(game_window, o_color, o_center, o_radius, o_width)
    pygame.display.update()


def generate_ai_move():
    global current_state
    guaranteed_best_value = -math.inf
    guaranteed_worst_value = math.inf
    print("AI is thinking!")
    ai_decided_state = get_best_state(current_state, find_depth(current_state), False,
                                      guaranteed_best_value, guaranteed_worst_value)[1]
    ai_decided_cell = get_move_index(current_state, ai_decided_state)
    put_o(ai_decided_cell)
    current_state = ai_decided_state


def ignore_mouse_click():
    for any_new_event in pygame.event.get():
        if any_new_event.type == pygame.MOUSEBUTTONDOWN:
            del any_new_event


pygame.init()
print("Welcome! Tic-Tac-Toe!")
game_window = create_game_window()
pygame.display.set_caption("TIC TAC TOE")
draw_grid(game_window)
reset_state()

while True:
    for any_event in pygame.event.get():
        if any_event.type == pygame.QUIT:
            print("Good Bye! Loser!")
            sys.exit()
        if any_event.type == pygame.MOUSEBUTTONDOWN:
            if check_click_validity(any_event.pos):
                target_cell = decide_cell(any_event.pos)
                if current_state[target_cell[0]][target_cell[1]] == 0:
                    current_state[target_cell[0]][target_cell[1]] = 1
                    put_x(target_cell)
                    pygame.time.wait(100)
                    if evaluate_state(current_state) is not None:
                        print("Game Over!")
                        reset_game_window()
                        continue
                    generate_ai_move()
                    ignore_mouse_click()
                    if evaluate_state(current_state) is not None:
                        print("Game Over!")
                        reset_game_window()
                        