class GomokuGame:
    def __init__(self, board_size=15):
        self.BOARD_SIZE = board_size
        self.reset_game()

    def reset_game(self):
        self.board = [[None for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_turn = 'black'
        self.game_over = False
        self.is_ai_thinking = False

    def check_win(self, row, col):
        stone = self.board[row][col]
        if stone is None: return False
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE and self.board[r][c] == stone:
                    count += 1
                else: break
            for i in range(1, 5):
                r, c = row - dr * i, col - dc * i
                if 0 <= r < self.BOARD_SIZE and 0 <= c < self.BOARD_SIZE and self.board[r][c] == stone:
                    count += 1
                else: break
            if count >= 5: return True
        return False

    def do_place_stone(self, row, col, available):
        if self.board[row][col] is None and not self.game_over:
            if not available:
                return False, None
            self.board[row][col] = self.current_turn
            if self.check_win(row, col):
                self.game_over = True
                return True, f"{self.current_turn.capitalize()} wins! (at {chr(ord('A')+col)}{row+1})"
            else:
                self.current_turn = 'white' if self.current_turn == 'black' else 'black'
                return False, f"Turn: {self.current_turn.capitalize()}"
        return False, None 