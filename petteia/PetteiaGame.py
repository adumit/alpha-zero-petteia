import sys
import logging
sys.path.append('..')

import typing as ta
import copy

import numpy as np

from Game import Game


log = logging.getLogger(__name__)

Move = ta.Tuple[ta.Tuple[int, int], ta.Tuple[int, int]]


class PetteiaGame(Game):
    def __init__(self):
        pass

    def create_board(self) -> np.array:
        grid = [[0 for i in range(8)] for j in range(8)]
        for index in range(8):
            grid[0][index] = -1
            grid[7][index] = 1 
        return np.array(grid)

    def update_board(self, game_grid: np.array, player: int, update_move: Move) -> np.array:
        copy_grid = copy.deepcopy(game_grid)
        former_loc = (update_move[0][0], update_move[0][1])
        new_loc = (update_move[1][0], update_move[1][1])
        log.debug(f"Update move: {update_move}")

        piece_val = copy_grid[former_loc[0]][former_loc[1]]
        try:
            assert piece_val == player
        except AssertionError as e:
            self.print_board(game_grid)
            print(f"Player: {player}, move={update_move}")
            raise e
        copy_grid[former_loc[0]][former_loc[1]] = 0
        copy_grid[new_loc[0]][new_loc[1]] = piece_val
        if piece_val > 0:
            for capped in self.find_captures(copy_grid, new_loc, 1):
                # The value returned by find captures will be the negative index within the enemy teams list
                copy_grid[capped[0]][capped[1]] = 0
        else:
            for capped in self.find_captures(copy_grid, update_move[1], -1):
                # The value returned by find captures will be the negative index within the enemy teams list
                copy_grid[capped[0]][capped[1]] = 0
        return copy_grid

    def generate_capture_moves(self, board: np.array, move_list: ta.List[Move], player: int):
        move_locations = [m[1] for m in move_list]
        capture_outcomes = [m for m in move_locations if self.find_captures(board, m, player)]
        return [m for m in move_list if m[1] in capture_outcomes]


    def find_captures(self, grid, piece_location, team):
        return self.check_capture_direction_NS(grid, piece_location, team, range(piece_location[0]-1, -1, -1)) + \
               self.check_capture_direction_NS(grid, piece_location, team, range(piece_location[0]+1, 8)) + \
               self.check_capture_direction_EW(grid, piece_location, team, range(piece_location[1]-1, -1, -1)) + \
               self.check_capture_direction_EW(grid, piece_location, team, range(piece_location[1]+1, 8))

    def check_capture_direction_NS(self, grid, piece_location, team, search_spaces):
        potential_capture = []
        for i in search_spaces:
            # piece type is the index of the piece, with positivity indicating same team, and negativity the opposite
            piece_type = team*grid[i][piece_location[1]]
            if piece_type < 0:
                potential_capture.append((i, piece_location[1]))
            elif piece_type == 0:
                break
            else:
                return potential_capture
        return []

    def check_capture_direction_EW(self, grid, piece_location, team, search_spaces):
        potential_capture = []
        for i in search_spaces:
            # piece type is the index of the piece, with positivity indicating same team, and negativity the opposite
            piece_type = team*grid[piece_location[0]][i]
            if piece_type < 0:
                potential_capture.append((piece_location[0], i))
            elif piece_type == 0:
                break
            else:
                return potential_capture
        return []

    def generate_moves(self, board, player, debug: bool = False) -> ta.List[ta.Tuple[ta.Tuple[int, int], ta.Tuple[int, int]]]:
        possible_moves = []
        x_pos, y_pos = np.array(board == player).nonzero()
        pos_positions = list(zip(x_pos, y_pos))
        if debug:
            print(f"Player:", player)
            self.print_board(board)
            print(f"X_pos={x_pos}, Y_pos={y_pos}")
            print("Pos positions:", pos_positions)

        for piece in pos_positions:
            # For moving forward
            for i in range(piece[0]-1, -1, -1):
                if board[i][piece[1]] == 0:
                    possible_moves.append((piece, (i, piece[1])))
                else:
                    break
            # For moving backwards
            for i in range(piece[0]+1, 8):
                if board[i][piece[1]] == 0:
                    possible_moves.append((piece, (i, piece[1])))
                else:
                    break
            # For moving left
            for i in range(piece[1]-1, -1, -1):
                if board[piece[0]][i] == 0:
                    possible_moves.append((piece, (piece[0], i)))
                else:
                    break
            # For moving right
            for i in range(piece[1]+1, 8):
                if board[piece[0]][i] == 0:
                    possible_moves.append((piece, (piece[0], i)))
                else:
                    break
        return possible_moves

    def print_board(self, grid, should_return=False):
        board_str = "    0   1   2   3   4   5   6   7   \n"
        for i in range(8):
            line_str = str(i) + " |"
            for j in range(8):
                if grid[i][j] < 0:
                    line_str += " - |"
                elif grid[i][j] > 0:
                    line_str += " + |"
                else:
                    line_str += "   |"
            board_str += line_str + "\n"
        if should_return:
            return board_str
        print(board_str)

    def convert_move_to_action(self, move, verbose=False):
        start_x, start_y = move[0]
        end_x, end_y = move[1]
        
        x_index = end_x - 1 if end_x > start_x else end_x
        y_index = end_y - 1 if end_y > start_y else end_y
        x_diff = abs(start_x - end_x)
        y_diff = abs(start_y - end_y)
        
        if verbose:
            print(f"x_index={x_index}, y_index={y_index}")
            print(f"x_diff={x_diff}, y_diff={y_diff}")
        
        return start_x * 112 + start_y * 14 + (x_index if x_diff else 0) + (7 + y_index if y_diff else 0)

    def convert_action_to_move(self, action, verbose=False):
        start_x = action // 112
        start_y = (action % 112) // 14
        remainder = action % 14
            
        end_x = remainder + (1 if remainder == start_x else 0) if remainder < 7 else start_x
        end_y = (remainder - 7) + (1 if (remainder - 7) == start_y else 0) if remainder >= 7 else start_y
        
        if verbose:
            print(f"remainder={remainder}")
            print(f"start_x={start_x}, start_y={start_y}")
            print(f"end_x={end_x}, end_y={end_y}")
        return ((start_x, start_y), (end_x, end_y))

    ############
    # Parent functions
    ############

    def getInitBoard(self) -> np.array:
        return self.create_board()

    def getBoardSize(self) -> ta.Tuple[int, int]:
        return 8, 8

    def getActionSize(self) -> int:
        return 64 * 14

    def getValidMoves(self, board, player, debug=False) -> np.array:
        generated_moves = self.generate_moves(board, player, debug=debug)
        valid_moves_from_action_size = np.zeros(self.getActionSize())
        # The action size is 64 * 14. The first 14 are for the first square, the next 14 are for the second square, etc.
        # The first square is the bottom left, the last square is the top right.
        for move in generated_moves:
            action_position = self.convert_move_to_action(move)
            valid_moves_from_action_size[action_position] = 1
            
        return valid_moves_from_action_size

    def getNextState(self, board, player, action) -> ta.Tuple[np.array, int]:
        # The action size is 64 * 14. The first 14 are for the first square, the next 14 are for the second square, etc.
        # The first square is the bottom left, the last square is the top right.
        start_pos, end_pos = self.convert_action_to_move(action)
        move = (start_pos, end_pos)
        try:
            new_board = self.update_board(board, player, move)
        except (RecursionError, AssertionError) as e:
            self.print_board(board)
            print(f"Player: {player}, move={move}")
            print("Valid moves:", self.getValidMoves(board, 1, debug=True))
            raise e
        return new_board, -player

    def getGameEnded(self, board: np.array, player: int) -> int:
        # 1 or fewer pieces left
        if (board > 0).sum() <= 1:
            return -player
        # All pieces are trapped
        if len(self.generate_moves(board, player)) == 0:
            return -player
        return 0

    def getCanonicalForm(self, board, player) -> np.array:
        return board * player

    def getSymmetries(self, board, pi) -> ta.List[ta.Tuple[np.array, np.array]]:
        assert (len(pi) == self.getActionSize())
        pi_board = np.reshape(pi, (64, 14))
        l = [(board, list(pi_board.ravel()))]
        return l

    def stringRepresentation(self, board) -> str:
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        return self.print_board(should_return=True, grid=board)