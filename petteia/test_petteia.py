import pytest
import numpy as np


from .PetteiaGame import PetteiaGame


def test_generate_moves():
    game = PetteiaGame()
    moves = game.generate_moves(board=game.getInitBoard(), player=1)
    assert len(moves) == 6 * 8
    

def test_get_valid_moves():
    game = PetteiaGame()
    board = game.getInitBoard()
    valid_moves_from_start = game.getValidMoves(board, 1)
    game.print_board(board)
    print(valid_moves_from_start)
    assert sum(valid_moves_from_start) == 6 * 8
    assert valid_moves_from_start[844] == 1


def test_convert_move_to_action():
    game = PetteiaGame()
    
    all_positions = []
    for x in range(8):
        for y in range(8):
            all_positions.append((x , y))

    all_start_to_end = []
    for pos in all_positions:
        start_x, start_y = pos
        for new_x in range(8):
            if new_x == start_x:
                continue
            all_start_to_end.append(((start_x, start_y), (new_x, start_y)))
        for new_y in range(8):
            if new_y == start_y:
                continue
            all_start_to_end.append(((start_x, start_y), (start_x, new_y)))

    output_positions = []
    for start, end in all_start_to_end:
        output_positions.append(game.convert_move_to_action((start, end)))
    assert len(output_positions) == len(set(output_positions))


def test_convert_action_to_move():
    game = PetteiaGame()
    for action in range(896):
        start, end = game.convert_action_to_move(action)
        if not 0 <= start[0] <= 7:
            print("Throw 1")
            print(action, start, end)
            break
        elif not 0 <= start[1] <= 7:
            print("Throw 2")
            print(action, start, end)
            break
        elif not 0 <= end[0] <= 7:
            print("Throw 3")
            print(action, start, end)
            break
        elif not 0 <= end[1] <= 7:
            print("Throw 4")
            print(action, start, end)
            break


def test_get_canonical_form():
    game = PetteiaGame()
    board = game.getInitBoard()
    canonical_board = game.getCanonicalForm(board, 1)
    assert np.array_equal(board, canonical_board)
    canonical_board = game.getCanonicalForm(board, -1)
    assert np.array_equal(board, -canonical_board)


def test_make_move():
    game = PetteiaGame()
    board = game.getInitBoard()
    outcome_board, next_player = game.getNextState(board, 1, 895)
    game.print_board(outcome_board)
    assert next_player == -1
    assert outcome_board[7, 6] == 1
    assert outcome_board[7, 7] == 0


def test_action_conversion():
    game = PetteiaGame()

    base_move = ((0, 0), (0, 1))
    action_from_move = game.convert_move_to_action(base_move)
    move_from_action = game.convert_action_to_move(action_from_move)
    assert base_move == move_from_action

    start_action = 0
    move_from_action = game.convert_action_to_move(start_action, verbose=True)
    print(move_from_action)
    action_from_move = game.convert_move_to_action(move_from_action, verbose=True)
    assert start_action == action_from_move
    
    start_action = 1
    move_from_action = game.convert_action_to_move(start_action, verbose=True)
    print(move_from_action)
    action_from_move = game.convert_move_to_action(move_from_action, verbose=True)
    assert start_action == action_from_move

    for action in range(896):
        start, end = game.convert_action_to_move(action)
        new_action = game.convert_move_to_action((start, end))
        try:
            assert action == new_action
        except AssertionError as e:
            print(f"Start,end={start},{end} action={action} new_action={new_action}")
            raise e