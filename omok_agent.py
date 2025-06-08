import json
from litellm import completion
from pydantic import BaseModel, Field
from dotenv import dotenv_values

config = dotenv_values(".env")

class OmokMove(BaseModel):
    row: int = Field(..., description="The row of the move (0-based index)")
    col: int = Field(..., description="The column of the move (0-based index)")

def omok_chat_completion(board):

    # 보드를 문자열로 변환
    board_str = str(format_board_as_matrix(board))
    messages = [
        {
    "role": "system",
    "content": """당신은 세계 최고 수준의 바둑 및 오목(Gomoku) AI입니다. 당신의 임무는 주어진 바둑판 상태를 분석하여 최선의 다음 수를 결정하는 것입니다.

    
네, 알겠습니다. AI에게 오목 규칙을 명확하게 알려주기 위한 프롬프트용 텍스트입니다. 간결하고 구조화된 형태로 정리했습니다.

이 내용을 시스템 프롬프트에 추가하여 AI가 게임 규칙을 정확히 따르도록 지시할 수 있습니다.

---

### 오목(Gomoku) 게임 규칙 (AI용)

**1. 게임 목표**
- 가로, 세로, 또는 대각선 방향으로 자신의 돌 다섯 개를 먼저 연속으로 놓으면 승리합니다.

**2. 진행 방식**
- 흑돌이 첫 수를 둡니다.
- 서로 번갈아 가며 교차점에 돌을 하나씩 놓습니다.
- 한번 둔 돌은 움직일 수 없습니다.

**3. 승리 조건: 오목(五目)**
- 자신의 돌 5개를 가로, 세로, 대각선 중 한 방향으로 일렬로 놓으면 즉시 승리합니다.

**4. 흑(Black)의 금수(禁手, Forbidden Moves)**
- 아래의 규칙은 오직 **흑에게만 적용**됩니다. 백은 금수가 없습니다.
- 흑이 금수 위치에 돌을 놓으면 패배합니다.

- **3-3 (삼삼)**
  - 한 수를 두었을 때 '열린 3'이 동시에 2개 이상 만들어지는 자리.
  - '열린 3'이란, 양쪽으로 한 칸씩 더 놓아 '4'를 만들 수 있는 3개의 돌 배열을 의미합니다. (예: `.OOO.`)

- **4-4 (사사)**
  - 한 수를 두었을 때 '4'가 동시에 2개 이상 만들어지는 자리.

- **장목(長目, Overline)**
  - 6개 이상의 돌을 연속으로 놓는 것. 흑은 장목으로 승리할 수 없습니다. (게임은 계속됩니다.)



### 바둑판 표현 방식
바둑판은 숫자 값으로 이루어진 2차원 행렬(리스트의 리스트) 형식으로 제공됩니다.

1은 흑돌을 나타냅니다.
-1은 백돌을 나타냅니다.
0은 비어있는 칸을 나타냅니다.

당신은 흰색돌 입니다.

### 당신의 임무
1.  **바둑판 분석:** 흑돌과 백돌의 모든 위치를 신중하게 검토합니다.
2.  **최선의 수 결정:** 승리하거나 상당한 우위를 점하기 위해 돌을 놓을 가장 전략적인 빈칸을 찾습니다.
3.  **JSON 형식으로 응답:** 당신의 답변은 *반드시* JSON 객체로만 제공해야 합니다.

### 출력 요구사항 (매우 중요)
당신의 JSON 응답은 반드시 'row'와 'col' 필드를 포함해야 하며, 이 값들은 당신이 선택한 수의 **0부터 시작하는 정수 인덱스(0-based integer index)**여야 합니다.

**좌표 변환 예시:**
- 좌표 **A1**에 수를 두는 것은 `{"row": 0, "col": 0}`에 해당합니다.
- 좌표 **C4**에 수를 두는 것은 `{"row": 3, "col": 2}`에 해당합니다.
- 좌표 **O15**에 수를 두는 것은 `{"row": 14, "col": 14}`에 해당합니다.

응답에 다른 텍스트, 설명, 또는 대화형 문구를 절대로 추가하지 마십시오.
"""
},
        {"role": "user", "content": f"""The current board is: {board_str}
        Make your move as white stone."""},
    ]
    openai_api_key = config["OPENAI_API_KEY"]
    gemini_api_key = config["GEMINI_API_KEY"]
    
    response = completion(
        model="gemini/gemini-2.5-flash-preview-05-20", #gpt-4o
        api_key=gemini_api_key,
        messages=messages,
        response_format=OmokMove
    )
    
    try:
        json_response = json.loads(response.choices[0].message.content)
        return OmokMove(**json_response)
    except Exception as e:
        print(f"Error parsing AI response: {e}")
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