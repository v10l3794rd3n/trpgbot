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
        _script += f'"{_name}, 힘든 일이 있으면 언제든 알려줘!'
    elif _house == 'S': #성
        _script += f'"너무 귀찮은 일은 만들지 말도록, {_surname}."'
    elif _house == 'R': #이름
        _script += f'"내가 그리핀도르 사감 교수님 도마뱀으로 만든 거, 누가 일렀어?!"'
    elif _house == 'H': #성
        _script += f'"즐거운 학기 보내게, {_surname} 학생."'
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
    return ''.join(f"{key}{int(value)}" for key, value in sorted(d.items()))


def make_farming_script(pc_id, code):
    _script = ""
    _id = pc_id
    _code = decimal_to_hex(code) # 10진법을 16진법으로 변환

    _inventory = parse_string_to_dict(_code)

#    s = re.search(r"a/(.*?)\]", _code)
    
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


gacha = [
    '포도사탕', '용 모양 미니어처', '[용사 이야기]라는 제목의 동화책', '반지', '목걸이', '스카프', '리본', '나비 머리핀', '새(bird) 인형',
    '설탕 깃펜', '피징 위즈비', '비법 노트', '들꽃', '설탕에 절인 제비꽃', '감초사탕', '가짜 손', '물감', '초콜릿', '작은 펭귄인형', '다 낡은 "마법의 역사"책', '알 수 없는 로맨스 소설책',
    '딸기 케이크', '민달팽이 젤리', '맑은 구슬', '만년필', '잉크', '애플시나몬파이',
    '쿠키' '화분' '흰색 깃펜', '설탕 캔디', '손거울', '시트러스 향 향수', '레몬잼', '토스트', '새 모형',
    '솜사탕', '파란 리본', '미니 플라네타리움', '사탕 단지', '꿀을 넣은 패스츄리', '병아리 인형',
    '두꺼운 책' , '소라껍데기' , '반짝이는 보석', '손수건', '만년필', '은하수 모형', 
    '드림캐쳐', '옴니큘러', '움직이는 동물 모양 액션 피겨', '토마토 카프레제', '골동품 시계' '스노우 볼',
    '마시멜로우 핫초코','속기 깃펜','두꺼운 논문 책', '귀마개', '인형', '커피', '테오도르 증명사진' , '사진첩' , '잉크',
    '수르스트뢰밍' '[마법사에 대한 고찰]이라는 제목의 글씨가 많고 두꺼운 책' '사탕 모양 장식품',
    '파리채', '해면 수세미', '벌어진 칫솔', '구토맛 젤리', '매운 맛 사탕', '부부젤라',
    '커피', '감초 맛 사탕', '바퀴벌레 과자', '구토맛 젤리', '회초리', '칼',
    '샐러드', '백과사전', '털장갑과 목도리', '모래시계', '시든 장미꽃 한송이',
    '감초 사탕', '정어리 파이', '우유', '정어리 파이', '신을 형상화한 작은 장식품',
    '당근젤리', '태엽인형', '가십지', '블랙 푸딩', '조화(造花)', '달팽이',
    '금화 초콜릿', '모조 보석', '인테리어 소품', '과제', '오트밀', '루빅스 큐브',
    '귀지맛 젤리', '구토맛 젤리', '먹음직스러운 가짜 사탕', '거대 바퀴벌레 모형',
    '벌레 모형', '키가 쑥쑥! 성장 발육제', '깜짝 상자', '시끄러운 장난감' , '미지근한 우유' , '찢어진 책',
    '감초사탕', '하울러', '마법사 체스세트', '흙 맛 젤리빈', '하울러', '폭탄카드',
    '설탕 츄러스', '캐러멜' '부러진 깃펜', '로맨스 소설책', '거미모양 장난감','설탕 깃펜',
    '스니치', '넥타이', '연애편지', '뱀 허물', '썩은 달걀 맛 강낭콩 젤리', '정어리'
]


def make_gacha_script(s):
    _script = ""
    _script += '랜덤박스를 열면, 그 안에는...\n\n'
    for n in range(s):
        _script += '짜잔! ' + random.choice(gacha) +'!\n'
    _script += '\n물론, 어디까지나 장난감이지만!'

    return _script

def make_inventory_script(s):
    _script = ""
    _code = decimal_to_hex(s) # 10진법을 16진법으로 변환

    _inventory = parse_string_to_dict(_code)

    s = re.search(r"a/(.*?)\]", _code)
    

    _script += '현재 소지 재료\n\n'
    _script += f'호클럼프 즙: {_inventory['a']}\n'
    _script += f'박하 잎: {_inventory['b']}\n'
    _script += f'거미 털: {_inventory['c']}\n'
    _script += f'독버섯 갓: {_inventory['d']}\n'
    _script += f'풀잠자리: {_inventory['e']}\n'
    _script += f'보름초 줄기: {_inventory['f']}\n'

    return _script

def make_potion_script(s, potion):
    _script = ""
    _code = decimal_to_hex(s)  # 10진법을 16진법으로 변환
    _potion = potion

    print(f"🎯 원본 10진수 인벤토리 코드: {s}")
    print(f"🎯 변환된 16진수 인벤토리 코드: {_code}")

    _inventory = parse_string_to_dict(_code)

    print(f"🎯 16진수를 딕셔너리로 변환한 결과: {_inventory}")

    _script += f'{_potion}, 만들어 봅시다!\n\n'

    potion_requirements = {
        '아르부스': {'a': 2, 'b': 1},
        '파이제논': {'e': 2, 'f': 1},
        '폴리주스': {'b': 2, 'c': 1},
        '티르소스': {'c': 2, 'd': 1},
        '비즈둔': {'d': 2, 'e': 1},
        '메이고르': {'f': 2, 'a': 1}
    }

    if _potion not in potion_requirements:
        _script += '혹시 마법약 이름을 틀리진 않았을까?'
        return _script

    requirements = potion_requirements[_potion]

    for ingredient, amount in requirements.items():
        if _inventory.get(ingredient, 0) < amount:
            _script += '재료가 부족해! 다시 확인해 보자.'
            return _script

    for ingredient, amount in requirements.items():
        _inventory[ingredient] -= amount

    potion_effects = {
        '아르부스': '이제 둥둥 떠다닐 수 있어!',
        '파이제논': '이걸로 공부의 신이 되자.',
        '폴리주스': '머리카락만 슬쩍 훔쳐오면 나도...',
        '티르소스': '이제 졸아도 안 들킨다고!',
        '비즈둔': '초코가 좋아.',
        '메이고르': '이걸로 좋은 하루가 될 거야!'
    }
    
    _script += potion_effects[_potion]

    _code = dict_to_hex_string(_inventory)
    print(f"🎯 수정된 딕셔너리를 16진수로 변환한 결과: {_code}")

    _code = hex_to_decimal(_code)
    print(f"🎯 최종적으로 변환된 10진수 인벤토리 코드: {_code}")

    _script += f'\n\n인벤토리 코드: {_code}'

    return _script



card = {
    '아라벨라': '빗자루',
    '트루먼': '지팡이',
    '리키': '빗자루',
    '펠릭스': '지팡이',
    '다아시': '빗자루',
    '테오도르': '지팡이',
    '엘리오르': '빗자루',
    '에셀레드': '지팡이',
    '리아트리스': '빗자루',
    '노라': '지팡이',
    '벤자민': '빗자루',
    '나샤렛': '지팡이',
    '에블린': '빗자루',
    '이엔': '지팡이',
    '러셀': '빗자루',
    '주노': '지팡이',
    '에밀리': '빗자루',
    '애슈턴': '지팡이',
    '이사야': '빗자루',
    '밋치': '지팡이',
    '일': '빗자루',
    '아니카': '지팡이'
}

def make_hgsmd_change_script(s, id):
    _name = s
    _changer = profile[id][1]
    _script = '서로 카드를 바꿉니다. 무슨 일이 일어날까요?'

    save = card[_changer]
    card[_changer] = card[_name]
    card[_name] = save

    print(card)

    return _script

def make_hgsmd_result_script(s, id):
    _name = profile[id][1]
    _script = f'정답은... {card[_name]}!\n\n'

    if s == card[_name]:
        _script += '정답! 선물을 받아가자.\n\n스토리 계정으로 멘션 부탁드립니다.'
    else:
        _script += '오답! 아쉽게 됐다... 1갈레온을 획득합니다.'

    return _script
    

profile = {
    'Arabella': ['G', '아라벨라', '아라벨라', '가', '를'],
    'Truman_Adams': ['H', '트루먼', '애덤스', '이', '을'],
    'Ricky': ['S', '리키', '에어드', '가', '를'],
    'FelixPB': ['S', '펠릭스', '베넷', '가', '를'],
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
    '_RP_00': ['S', '러셀', '패트릭', '이', '을'],
    'jono': ['R', '주노', '바브렉', '가', '를'],
    'EmilyLT': ['H', '에밀리', '로랑', '가', '를'],
    'AG': ['S', '애슈턴', '매버릭', '이', '을'],
    'Isaiah_': ['R', '이사야', '서머스', '가', '를'],
    'Mitch': ['R', '밋치', '린도', '가', '를'],
    '3_lines': ['H', '일', '커스버트슨', '이', '을'],
    'anika': ['G', '아니카', '리', '가', '를']
}