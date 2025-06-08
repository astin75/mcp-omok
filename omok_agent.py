import json
from litellm import completion
from pydantic import BaseModel, Field
from dotenv import dotenv_values

config = dotenv_values(".env")

# 사용 가능한 AI 모델 목록
AVAILABLE_MODELS = [
    'openai/gpt-4o',
    'openai/gpt-4o-mini',
    'openai/o4-mini',
    'gemini/gemini-2.0-flash',
    'gemini/gemini-2.5-flash-preview-05-20',
    'gemini/gemini-2.5-pro-preview-06-05',
]

class OmokMove(BaseModel):
    row: int = Field(..., description="The row of the move (0-based index)")
    col: int = Field(..., description="The column of the move (0-based index)")

def omok_chat_completion(board, model='gemini/gemini-2.5-pro-exp-0827'):
    # 보드를 문자열로 변환
    board_str = '\n'.join([''.join(['B' if cell == 'black' else 'W' if cell == 'white' else '.' for cell in row]) for row in board])
    
    messages = [
        {"role": "system", "content": """You are a professional omok player. You are given a board and you need to make a move.
        The board is represented as follows:
        - 'B' represents a black stone
        - 'W' represents a white stone
        - '.' represents an empty cell
        You should respond with a JSON object containing 'row' and 'col' fields, representing the 0-based indices of your move."""},
        {"role": "user", "content": f"The current board is:\n{board_str}\n\nMake your move as white stone."},
    ]
    
    try:
        print(f"AI is thinking with model: {model}")
        response = completion(
            model=model,
            messages=messages,
            response_format={"type": "json_object"}
        )
        print(f"AI response: Done")
        
        move = OmokMove.model_validate_json(response.choices[0].message.content)
        return move
    except Exception as e:
        print(f"Error in AI response: {e}")
        return None

def format_board_as_matrix(board):
    """보드를 숫자 행렬(list of lists)로 변환합니다."""
    matrix = []
    for row in board:
        new_row = []
        for cell in row:
            if cell == 'black':
                new_row.append(1)   # 흑돌은 1
            elif cell == 'white':
                new_row.append(-1)  # 백돌은 -1
            else:
                new_row.append(0)   # 빈칸은 0
        matrix.append(new_row)
    return matrix

# AI에게 전달될 데이터 예시 (문자열로 변환)
# board_data_for_ai = str(format_board_as_matrix(state['board']))