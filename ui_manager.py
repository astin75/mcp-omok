from nicegui import ui
from game import GomokuGame
from omok_agent import omok_chat_completion

class GomokuUI:
    def __init__(self):
        self.game = GomokuGame()
        self.CELL_SIZE = 36
        self.STONE_SIZE = 30
        self.LABEL_AREA_SIZE = 30
        self.game_mode = 'pvp'  # 'pvp' 또는 'ai'
        self.setup_ui()

    def setup_ui(self):
        ui.query('body').style('align-items: center; justify-content: center;')
        with ui.header(elevated=True).classes('items-center justify-between w-full'):
            ui.label('오목 게임 (Gomoku)').classes('text-h5')
            with ui.row().classes('gap-4'):
                # 모드 선택 드롭다운을 먼저 생성
                self.mode_select = ui.select(
                    ['PvP (사람 vs 사람)', 'PvE (사람 vs AI)'],
                    value='PvP (사람 vs 사람)',
                    on_change=self.change_game_mode
                ).classes('w-48')
                ui.button("New Game", on_click=self.start_new_game, color='primary')
        
        self.turn_label = ui.label().classes('text-xl font-bold mt-20 mb-4')
        self.update_turn_label()
        self.create_board()

    def update_turn_label(self):
        mode_text = "PvP" if self.game_mode == 'pvp' else "PvE"
        player_text = "Human" if (self.game_mode == 'pvp' or self.game.current_turn == 'black') else "AI"
        self.turn_label.set_text(f"Mode: {mode_text} | Turn: {self.game.current_turn.capitalize()} ({player_text})")

    def change_game_mode(self, e):
        # 이벤트 객체에서 선택된 값을 가져옴
        selected_mode = e.value
        self.game_mode = 'pvp' if selected_mode == 'PvP (사람 vs 사람)' else 'ai'
        self.start_new_game()
        ui.notify(f"게임 모드가 {selected_mode}로 변경되었습니다.", color='info')

    def create_board(self):
        with ui.column().classes('items-center'):
            with ui.element('div').classes('p-4 rounded-lg shadow-lg').style('background-color: #D2B48C;'):
                # X축 좌표
                with ui.row().classes('gap-0').style(f'margin-left: {self.LABEL_AREA_SIZE}px;'):
                    for i in range(self.game.BOARD_SIZE):
                        with ui.element('div').classes('flex items-center justify-center').style(f'width:{self.CELL_SIZE}px; height:{self.LABEL_AREA_SIZE}px;'):
                            ui.label(chr(ord('A') + i)).classes('text-sm font-sans font-bold')

                # Y축 좌표와 보드
                with ui.row().classes('gap-0 items-center'):
                    # Y축 좌표
                    with ui.column().classes('gap-0'):
                        for i in range(self.game.BOARD_SIZE):
                            with ui.element('div').classes('flex items-center justify-center').style(f'width:{self.LABEL_AREA_SIZE}px; height:{self.CELL_SIZE}px;'):
                                ui.label(i + 1).classes('text-sm font-sans font-bold')
                    
                    # 게임 보드
                    self.create_game_board()

    @ui.refreshable
    def create_game_board(self):
        BOARD_DIM = self.CELL_SIZE * (self.game.BOARD_SIZE - 1)
        with ui.element('div').classes('relative').style(f'width:{BOARD_DIM}px; height:{BOARD_DIM}px;'):
            self.draw_grid_lines()
            self.draw_star_points()
            self.draw_stones()

    def draw_grid_lines(self):
        for i in range(self.game.BOARD_SIZE):
            ui.element('div').classes('absolute bg-black').style(f'left:{i * self.CELL_SIZE - 1}px; top:0; width:1.5px; height:100%;')
            ui.element('div').classes('absolute bg-black').style(f'top:{i * self.CELL_SIZE - 1}px; left:0; height:1.5px; width:100%;')

    def draw_star_points(self):
        star_points = [3, 11] if self.game.BOARD_SIZE > 7 else []
        if self.game.BOARD_SIZE % 2 == 1:
            center = (self.game.BOARD_SIZE - 1) // 2
            if center not in star_points: star_points.append(center)
        for r in star_points:
            for c in star_points:
                ui.element('div').classes('absolute bg-black rounded-full z-10').style(f'left:{c * self.CELL_SIZE - 4}px; top:{r * self.CELL_SIZE - 4}px; width:8px; height:8px;')

    def draw_stones(self):
        for r in range(self.game.BOARD_SIZE):
            for c in range(self.game.BOARD_SIZE):
                with ui.element('div').classes('absolute flex items-center justify-center').style(f'left:{c * self.CELL_SIZE - self.CELL_SIZE//2}px; top:{r * self.CELL_SIZE - self.CELL_SIZE//2}px; width:{self.CELL_SIZE}px; height:{self.CELL_SIZE}px; z-index: 20;'):
                    stone = self.game.board[r][c]
                    if stone == 'black':
                        ui.element('div').classes('rounded-full shadow-lg').style(f'width:{self.STONE_SIZE}px; height:{self.STONE_SIZE}px; background: radial-gradient(circle at 10px 10px, #555, #000);')
                    elif stone == 'white':
                        ui.element('div').classes('rounded-full shadow-lg').style(f'width:{self.STONE_SIZE}px; height:{self.STONE_SIZE}px; background: radial-gradient(circle at 10px 10px, #fff, #ccc);')
                    else:
                        ui.button(on_click=lambda r=r, c=c: self.place_stone(r, c)).props('flat round dense').classes('w-full h-full opacity-0 hover:opacity-40').style(f'background-color: {self.game.current_turn}; border-radius: 50%;')

    def place_stone(self, r: int, c: int):
        game_over, message = self.game.place_stone(r, c)
        self.create_game_board.refresh()
        
        if game_over:
            ui.notify(message, color='positive', position='center', multi_line=True, classes='text-h6')
            self.turn_label.set_text('Game Over')
        elif message:
            self.update_turn_label()
            
            # AI 모드이고 흰 돌 차례일 때 AI의 수를 둠
            if self.game_mode == 'ai' and self.game.current_turn == 'white' and not game_over:
                self.make_ai_move()

    def make_ai_move(self, is_random=False):
        # AI의 수를 계산
        response = omok_chat_completion(self.game.board)
        # TODO: AI 응답을 파싱하여 실제 수를 두는 로직 구현
        # 임시로 랜덤한 위치에 수를 두도록 구현
        if is_random:
            import random
            empty_positions = [(r, c) for r in range(self.game.BOARD_SIZE) 
                            for c in range(self.game.BOARD_SIZE) 
                            if self.game.board[r][c] is None]

            r, c = random.choice(empty_positions)
            self.place_stone(r, c)
        else:
            if response:
                self.place_stone(response.row, response.col)

    def start_new_game(self):
        self.game.reset_game()
        self.update_turn_label()
        self.create_game_board.refresh()
        ui.notify("새 게임이 시작되었습니다!", color='info') 