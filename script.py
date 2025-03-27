import random
import re
import os
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.utils.cell import coordinate_from_string, column_index_from_string


# random.range(0, 3) : 1~2
# random.choice(stat)

## 공통 함수

def find_cell_by_value(ws, keyword):
    for row in ws.iter_rows():
        for cell in row:
            if cell.value == keyword:
                return cell.coordinate  # 예: 'B2'

    return None  # 찾지 못했을 경우

def shift_cell(cell_ref: str, right=0, down=0) -> str:
    col_letter, row = coordinate_from_string(cell_ref)
    col_index = column_index_from_string(col_letter)

    new_col_index = col_index + right
    new_row = row + down

    if new_col_index < 1 or new_row < 1:
        raise ValueError("엑셀 범위를 벗어났습니다.")

    new_col_letter = get_column_letter(new_col_index)
    return f"{new_col_letter}{new_row}"

def get_shifted_cell_value(ws, base_cell: str, right=0, down=0):
    try:
        target_cell = shift_cell(base_cell, right, down)
        return ws[target_cell].value
    except ValueError as e:
        print(f"에러: {e}")
        return None


def get_offset_between_cells(from_cell: str, to_cell: str) -> tuple[int, int]:
    """
    두 셀 주소 간의 열/행 차이를 계산하여 (right, down) 튜플로 반환
    ex) C64 → AD64 → (right=27, down=0)
    """
    from_col_letter, from_row = coordinate_from_string(from_cell)
    to_col_letter, to_row = coordinate_from_string(to_cell)

    from_col_index = column_index_from_string(from_col_letter)  # C → 3
    to_col_index = column_index_from_string(to_col_letter)      # AD → 30

    right = to_col_index - from_col_index
    down = to_row - from_row

    return right, down

def roll_dice_expression(expr: str):
    """
    주사위 표현식(예: '2d6+1')을 계산해서 (굴림 결과, 최댓값) 반환
    """
    pattern = r"(\d*)d(\d+)([+-]\d+)?"
    match = re.fullmatch(pattern, expr.strip())

    if not match:
        raise ValueError(f"잘못된 표현식입니다: {expr}")

    num_dice = int(match.group(1)) if match.group(1) else 1  # 'd6' → 1d6 처리
    sides = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0

    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier
    max_possible = num_dice * sides + modifier

    return total, max_possible, rolls 


## CoC 구현

def CoC_dice(bonus: int = 0):
    original_roll = random.randint(1, 100)
    ones = original_roll % 10
    tens = original_roll // 10

    # 0~9로 처리 (10의 자리만)
    tens_candidates = [tens]

    for _ in range(abs(bonus)):
        roll = random.randint(0, 9)
        tens_candidates.append(roll)

    if bonus > 0:
        final_tens = max(tens_candidates)
    elif bonus < 0:
        final_tens = min(tens_candidates)
    else:
        final_tens = tens

    # 최종 결과
    result = final_tens * 10 + ones
    # 100 처리 (0 + 0 = 0은 실제로 100이니까)
    return 100 if result == 0 else result

def CoC_insane_now():
    number = random.randint(1, 10)
    result = f"🎲 1d10 = {number} | "
    if number == 1:
        result += "광기내용1"
    elif number == 2:
        result += "광기내용2"
    elif number == 3:
        result += "광기내용3"
    elif number == 4:
        result += "광기내용4"
    elif number == 5:
        result += "광기내용5"
    elif number == 6:
        result += "광기내용6"
    elif number == 7:
        result += "광기내용7"
    elif number == 8:
        result += "광기내용8"
    elif number == 9:
        result += "광기내용9"
    elif number == 10:
        result += "광기내용10"
    return result

def CoC_insane_summary():
    number = random.randint(1, 10)
    result = f"🎲 1d10 = {number} | "
    if number == 1:
        result += "광기내용1"
    elif number == 2:
        result += "광기내용2"
    elif number == 3:
        result += "광기내용3"
    elif number == 4:
        result += "광기내용4"
    elif number == 5:
        result += "광기내용5"
    elif number == 6:
        result += "광기내용6"
    elif number == 7:
        result += "광기내용7"
    elif number == 8:
        result += "광기내용8"
    elif number == 9:
        result += "광기내용9"
    elif number == 10:
        result += "광기내용10"
    return result

def CoC_damage(id, skill, modifier, tag):
    script = ""
    path = f'CoC/{id}.xlsx'

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active  # 또는 wb["시트이름"]

    cell = find_cell_by_value(ws, skill) # 무기 찾기
    print(skill)
    print(cell)

    r1, d1 = get_offset_between_cells('C62', 'Z62')
    damage = get_shifted_cell_value(ws, cell, right=r1, down=d1) #피해 찾기
    print(damage)
    r2, d2 = get_offset_between_cells('C62', 'S62')
    s = get_shifted_cell_value(ws, cell, right=r2, down=d2) # 판정 기능 찾기
    print(s)
    r3, d3 = get_offset_between_cells('C62', 'AD62')
    db = get_shifted_cell_value(ws, cell, right=r3, down=d3) # db 여부 찾기
    if db == 'db':
        bonus = ws['R29'].value
    else:
        bonus = False
    r4, d4 = get_offset_between_cells('C62', 'AV62')
    fail = get_shifted_cell_value(ws, cell, right=r4, down=d4) # 고장 가능성 찾기
    if isinstance(fail, (int, float)):
        broken = fail
    else:
        if isinstance(fail, str):
            try:
                int(fail)
                broken = fail
            except ValueError:
                broken = None
        else:
            broken = None
    # 판정
    s_c = find_cell_by_value(ws, s) # 기능 찾기
    print(s_c)
    r11, d11 = get_offset_between_cells('D40', 'K40')
    percent = get_shifted_cell_value(ws, s_c, right=r11, down=d11)
    r22, d22 = get_offset_between_cells('D40', 'M40')
    great = get_shifted_cell_value(ws, s_c, right=r22, down=d22)
    r33, d33 = get_offset_between_cells('D40', 'N40')
    extreme = get_shifted_cell_value(ws, s_c, right=r33, down=d33)

    result = CoC_dice(modifier)

    success = ""
    
    if result <= extreme:
        success = "극단적 성공"
    elif result <= great:
        success = "대단한 성공"
    elif result <= percent:
        success = "성공"
    else:
        success = "실패"
    if result == 1:
        success = "대성공"
    if result >= 96:
        if percent < 50:
            success = "대실패"
        else:
            if result == 100:
                success = "대실패"
    if broken:
        if result >= broken:
            success += "+고장"

    script += f"🎲 1d100 = {result} [{success}]"

    r, max_r, rolls = roll_dice_expression(damage)

    
    if success == "극단적 성공" or success == "대성공":
        if tag == '치명타':
            script += f" | {damage} = {rolls} → {r} + {max_r} 치명타!"
        else:
            script += f" | {damage} = {max_r}"
    elif success == "성공" or success == "대단한 성공":
        script += f" | {damage} = {rolls} → {r}"

    if bonus and bonus != "0":
        br, bmax_r, brolls = roll_dice_expression(bonus)
        if success == "극단적 성공" or success == "대성공":
            script += f" | db {bonus} = {bmax_r}"
        elif success == "성공" or success == "대단한 성공":
            script += f" | db {bonus} = {brolls} → {br}"

    return script


def CoC_stat(id, skill, modifier):
    script = ""
    path = f'CoC/{id}.xlsx'

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active  # 또는 wb["시트이름"]

    cell = find_cell_by_value(ws, skill) # 기능 찾기
    r1, d1 = get_offset_between_cells('X6', 'Z6')
    percent = get_shifted_cell_value(ws, cell, right=r1, down=d1)
    r2, d2 = get_offset_between_cells('X6', 'AD6')
    great = get_shifted_cell_value(ws, cell, right=r2, down=d2)
    r3, d3 = get_offset_between_cells('X6', 'AD8')
    extreme = get_shifted_cell_value(ws, cell, right=r3, down=d3)

    result = CoC_dice(modifier)

    success = ""
    
    if result <= extreme:
        success = "극단적 성공"
    elif result <= great:
        success = "대단한 성공"
    elif result <= percent:
        success = "성공"
    else:
        success = "실패"
    if result == 1:
        success = "대성공"
    if result >= 96:
        if percent < 50:
            success = "대실패"
        else:
            if result == 100:
                success = "대실패"

    script += f"🎲 1d100 = {result} [{success}]"
    return script

def CoC_skill(id, skill, modifier):
    script = ""
    path = f'CoC/{id}.xlsx'

    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb.active  # 또는 wb["시트이름"]

    cell = find_cell_by_value(ws, skill) # 기능 찾기
    r1, d1 = get_offset_between_cells('D40', 'K40')
    percent = get_shifted_cell_value(ws, cell, right=r1, down=d1)
    r2, d2 = get_offset_between_cells('D40', 'M40')
    great = get_shifted_cell_value(ws, cell, right=r2, down=d2)
    r3, d3 = get_offset_between_cells('D40', 'N40')
    extreme = get_shifted_cell_value(ws, cell, right=r3, down=d3)

    result = CoC_dice(modifier)

    success = ""
    
    if result <= extreme:
        success = "극단적 성공"
    elif result <= great:
        success = "대단한 성공"
    elif result <= percent:
        success = "성공"
    else:
        success = "실패"
    if result == 1:
        success = "대성공"
    if result >= 96:
        if percent < 50:
            success = "대실패"
        else:
            if result == 100:
                success = "대실패"

    script += f"🎲 1d100 = {result} [{success}]"
    return script

def CoC_sanity(sanity, modifier):
    percent = sanity
    great = sanity // 2
    extreme = sanity // 5

    result = CoC_dice(modifier)

    success = ""
    script = ""
    
    if result <= extreme:
        success = "극단적 성공"
    elif result <= great:
        success = "대단한 성공"
    elif result <= percent:
        success = "성공"
    else:
        success = "실패"
    if result == 1:
        success = "대성공"
    if result >= 96:
        if percent < 50:
            success = "대실패"
        else:
            if result == 100:
                success = "대실패"

    script += f"🎲 1d100 = {result} [{success}]"

    return script