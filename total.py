from nicegui import ui

# --- 기본 설정 및 게임 상태 ---
BOARD_SIZE = 15
state = {
    'board': [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
    'current_turn': 'black',
    'game_over': False,
}

# --- 게임 로직 함수 (변경 없음) ---
def check_win(row, col):
    stone = state['board'][row][col]
    if stone is None: return False
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        count = 1
        for i in range(1, 5):
            r, c = row + dr * i, col + dc * i
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and state['board'][r][c] == stone:
                count += 1
            else: break
        for i in range(1, 5):
            r, c = row - dr * i, col - dc * i
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and state['board'][r][c] == stone:
                count += 1
            else: break
        if count >= 5: return True
    return False

def place_stone(r, c):
    if state['board'][r][c] is None and not state['game_over']:
        state['board'][r][c] = state['current_turn']
        board_ui.refresh()
        if check_win(r, c):
            ui.notify(f"{state['current_turn'].capitalize()} wins! (at {chr(ord('A')+c)}{r+1})", 
                      color='positive', position='center', multi_line=True, classes='text-h6')
            state['game_over'] = True
            turn_label.set_text('Game Over')
        else:
            state['current_turn'] = 'white' if state['current_turn'] == 'black' else 'black'
            turn_label.set_text(f"Turn: {state['current_turn'].capitalize()}")

def start_new_game():
    state['board'] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    state['current_turn'] = 'black'
    state['game_over'] = False
    turn_label.set_text(f"Turn: {state['current_turn'].capitalize()}")
    board_ui.refresh()
    ui.notify("New game started!", color='info')

# --- 보드 UI를 그리는 함수 ---
@ui.refreshable
def board_ui():
    """선을 직접 그려서 보드를 생성하는 UI 함수 (좌표 제외)"""
    CELL_SIZE = 36
    STONE_SIZE = 30
    BOARD_DIM = CELL_SIZE * (BOARD_SIZE - 1)

    with ui.element('div').classes('relative').style(f'width:{BOARD_DIM}px; height:{BOARD_DIM}px;'):
        # 선 그리기
        for i in range(BOARD_SIZE):
            ui.element('div').classes('absolute bg-black').style(f'left:{i * CELL_SIZE - 1}px; top:0; width:1.5px; height:100%;')
            ui.element('div').classes('absolute bg-black').style(f'top:{i * CELL_SIZE - 1}px; left:0; height:1.5px; width:100%;')
        
        # 화점 그리기
        star_points = [3, 11] if BOARD_SIZE > 7 else []
        if BOARD_SIZE % 2 == 1:
            center = (BOARD_SIZE - 1) // 2
            if center not in star_points: star_points.append(center)
        for r in star_points:
            for c in star_points:
                ui.element('div').classes('absolute bg-black rounded-full z-10').style(f'left:{c * CELL_SIZE - 4}px; top:{r * CELL_SIZE - 4}px; width:8px; height:8px;')
        
        # 돌과 버튼 배치
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                with ui.element('div').classes('absolute flex items-center justify-center').style(f'left:{c * CELL_SIZE - CELL_SIZE//2}px; top:{r * CELL_SIZE - CELL_SIZE//2}px; width:{CELL_SIZE}px; height:{CELL_SIZE}px; z-index: 20;'):
                    stone = state['board'][r][c]
                    if stone == 'black':
                        ui.element('div').classes('rounded-full shadow-lg').style(f'width:{STONE_SIZE}px; height:{STONE_SIZE}px; background: radial-gradient(circle at 10px 10px, #555, #000);')
                    elif stone == 'white':
                        ui.element('div').classes('rounded-full shadow-lg').style(f'width:{STONE_SIZE}px; height:{STONE_SIZE}px; background: radial-gradient(circle at 10px 10px, #fff, #ccc);')
                    else:
                        ui.button(on_click=lambda r=r, c=c: place_stone(r, c)).props('flat round dense').classes('w-full h-full opacity-0 hover:opacity-40').style(f'background-color: {state["current_turn"]}; border-radius: 50%;')

# --- 최종 UI 레이아웃 ---
ui.query('body').style('align-items: center; justify-content: center;')
with ui.header(elevated=True).classes('items-center justify-between w-full'):
    ui.label('오목 게임 (Gomoku)').classes('text-h5')
    ui.button("New Game", on_click=start_new_game, color='primary')
turn_label = ui.label(f"Turn: {state['current_turn'].capitalize()}").classes('text-xl font-bold mt-20 mb-4')

# 보드와 좌표를 감싸는 전체 컨테이너
with ui.column().classes('items-center'):
    CELL_SIZE = 36
    LABEL_AREA_SIZE = 30  # 좌표가 표시될 영역의 크기

    # 나무 질감의 프레임
    with ui.element('div').classes('p-4 rounded-lg shadow-lg').style('background-color: #D2B48C;'):
        
        # 상단 X축 좌표 (A, B, C...)
        with ui.row().classes('gap-0').style(f'margin-left: {LABEL_AREA_SIZE}px;'):
            for i in range(BOARD_SIZE):
                with ui.element('div').classes('flex items-center justify-center').style(f'width:{CELL_SIZE}px; height:{LABEL_AREA_SIZE}px;'):
                    ui.label(chr(ord('A') + i)).classes('text-sm font-sans font-bold')

        # 중앙 영역 (Y축 좌표 + 보드)
        with ui.row().classes('gap-0 items-center'):
            # 왼쪽 Y축 좌표 (1, 2, 3...)
            with ui.column().classes('gap-0'):
                for i in range(BOARD_SIZE):
                    with ui.element('div').classes('flex items-center justify-center').style(f'width:{LABEL_AREA_SIZE}px; height:{CELL_SIZE}px;'):
                        ui.label(i + 1).classes('text-sm font-sans font-bold')
            
            # 실제 게임이 이뤄지는 보드판
            board_ui()


ui.run()