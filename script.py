import random
import re

# random.range(0, 3) : 1~2
# random.choice(stat)

def make_script(pc_id):
    _script = ""
    _id = pc_id
    _house = profile[_id][0]
    _name = profile[_id][1]
    _surname = profile[_id][2]

    if _house == 'G': #이름
        _script += f'"{_name}, 신학기의 시작이구나!'
    elif _house == 'S': #성
        _script += f'"4학년이라니. 시간이 참 빨라."'
    elif _house == 'R': #이름
        _script += f'"{_name}! 세상에, 방학은 잘 보냈어?"'
    elif _house == 'H': #성
        _script += f'"{_surname} 학생... 이군. 못 알아 볼 뻔 했네."'
    else:
        return 'ERR:01 @ellipsis'
    
    _script += f'\n\n{_name}에게 1갈레온이 지급됩니다.'

    return _script


farming = [
    '틈새에서 갈레온을 하나 발견합니다. 야호. 갈레온 +1',
    '이상한 상자를 열어 보면... 갈레온이 하나 있습니다. 갈레온 +1',
    '천 사이에 싸여 있던 갈레온을 하나 발견했습니다. 갈레온 +1',
    '이건... 호클럼프 즙이군요. 신기한 걸 찾았습니다. 호클럼프 즙 +1',
    '병을 하나 발견합니다. 안에 든 건... 호클럼프 즙 같네요. 호클럼프 즙 +1',
    '시원한 냄새가 납니다. 박하 잎을 하나 찾습니다. 박하 잎 +1',
    '정원 같은 구역을 발견합니다. 박하 잎을 하나 땄습니다. 박하 잎 +1',
    '이상한 털이네요. 어디에 쓰는 걸까요? 거미 털 +1',
    '이런 것도 마법약에 쓰이는 거겠죠? 거미 털 +1',
    '벽에 흰 버섯이 자라 있습니다. 이건... 독버섯 갓 +1',
    '물건 사이사이로 흰 버섯이 보입니다. 독버섯 갓 +1',
    '무언가 날아다닙니다... 잡았다! 풀잠자리 +1',
    '이것도 필요할까요? 하지만 잡았습니다. 풀잠자리 +1',
    '식물이 난 구역을 발견합니다. 보름초 줄기 +1',
    '유리병 안에 풀이 가득 담겨 있네요. 보름초 줄기 +1'
]

def parse_string_to_dict(s: str) -> dict:
    pattern = re.findall(r'([a-zA-Z])(\d+)', s)  # 문자와 숫자를 그룹화하여 찾기
    parsed_dict = dict((char, int(num)) for char, num in pattern)  # 명확한 dict 변환
    return parsed_dict

def decimal_to_hex(decimal_number):
    return hex(int(decimal_number))[2:]

def hex_to_decimal(hex_string):
    return int(hex_string, 16)

def dict_to_hex_string(d):
    return ''.join(f"{key}{decimal_to_hex(value)}" for key, value in d.items())

def make_farming_script(pc_id, code):
    _script = ""
    _id = pc_id
    _code = decimal_to_hex(code) # 10진법을 16진법으로 변환

    _inventory = parse_string_to_dict(_code)

    s = re.search(r"a/(.*?)\]", _code)
    
    _name = profile[_id][1]
    _ga = profile[_id][3]

    _script += f'{_name}{_ga} 필요의 방을 뒤적거립니다.\n\n'
    _farming = random.choice(farming)

    if '호클럼프 즙' in _farming:
        _inventory['a'] += 1
    elif '박하 잎' in _farming:
        _inventory['b'] += 1
    elif '거미 털' in _farming:
        _inventory['c'] += 1
    elif '독버섯 갓' in _farming:
        _inventory['d'] += 1
    elif '풀잠자리' in _farming:
        _inventory['e'] += 1
    elif '보름초 줄기' in _farming:
        _inventory['f'] += 1

    _script += _farming

    _code = dict_to_hex_string(_inventory)
    _code = hex_to_decimal(_code)

    _script += f'\n\n인벤토리 코드: {_code}'

    return _script

store = [
    '"구매 고마워!" 선배가 갈레온을 셉니다.',
    '"근데, 그거 어디에 쓸 거야?" 선배가 묻습니다.',
    '선배가 물건을 내어줍니다. "이걸로 내 일확천금의 꿈으로 더 가까이..." 일확천금은 그런 뜻이 아닐 텐데?!',
    '"휴, 얼마 전엔 교수님한테 들킬 뻔 했잖아." 선배가 툴툴댑니다.',
    '"감사합니다, 고객님! 자, 여깄어."'
]

def make_store_script(pc_id, goods):
    _script = ""
    _id = pc_id
    _goods = goods
    
    _name = profile[_id][1]
    _ga = profile[_id][3]

    _script += f'{_name}{_ga} 상점에서 물건을 삽니다. {_goods}... 어디에 써 볼까요?\n\n'
    _script += random.choice(store)

    return _script



profile = {
    'Arabella': ['G', '아라벨라', '아라벨라', '가', '를'],
    'Truman_Adams': ['H', '트루먼', '애덤스', '이', '을'],
    'Ricky': ['S', '리키', '에어드', '가', '를'],
    'FelixPB': ['S', '펠릭스', '베넷', '가', '를'],
    'W1': ['S', '파시오마티아', '오데트릴', '가', '를'],
    'DarcyIsm': ['G', '다아시', '이즈멜', '가', '를'],
    'TEO928': ['R', '테오도르', '러셀', '가', '를'],
    'Elior': ['R', '엘리오르', '티모테우스', '가', '를'],
    'Eddy_M': ['R', '에셀레드', '무어', '가', '를'],
    'psyche_lin': ['G', '리아트리스', '스노우', '가', '를'],
    'NoraHolloway': ['H', '노라', '할로웨이', '가', '를'],
    '6enjqm1n22': ['H', '벤자민', '로크', '이', '을'],
    'nasaret': ['G', '나샤렛', '브링클리', '이', '을'],
    'Evelyn': ['R', '에블린', '페레즈', '이', '을'],
    'En_L': ['H', '이엔', '레인', '이', '을'],
    'Gray_L': ['S', '리', '그레이', '가', '를'],
    '_RP_00': ['S', '러셀', '패트릭', '이', '을'],
    'jono': ['R', '주노', '바브렉', '가', '를'],
    'EmilyLT': ['H', '에밀리', '로랑', '가', '를'],
    'AG': ['S', '애슈턴', '매버릭', '이', '을'],
    'Isaiah_': ['R', '이사야', '서머스', '가', '를'],
    'Mitch': ['R', '밋치', '린도', '가', '를'],
    '3_lines': ['H', '일', '커스버트슨', '이', '을'],
    'anika': ['G', '아니카', '리', '가', '를']
}