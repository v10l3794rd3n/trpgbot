import random

# random.range(0, 3) : 1~2
# random.choice(stat)

def make_script(pc_id):
    _script = ""
    _id = pc_id
    _house = profile[_id][0]
    _name = profile[_id][1]
    _surname = profile[_id][2]

    if _house == 'G':
        _script += f'사감 선생님이 인사합니다. "오늘도 좋은 하루 보내렴, {_name}."'
    elif _house == 'S':
        _script += f'사감 선생님이 고개를 끄덕입니다. "그래, 확인했다, {_surname}."'
    elif _house == 'R':
        _script += f'사감 선생님이 웃어줍니다. "좋은 하루! 기쁘게 보냈어, {_name}도?"'
    elif _house == 'H':
        _script += f'사감 선생님이 손을 흔듭니다. "{_surname} 학생, 좋은 하루 보내게."'
    else:
        return 'ERR:01 @ellipsis'

    return _script

Gryffindor = []
Ravenclaw = []
Hufflepuff = []
Slytherin = []

profile = {
    'Arabella': ['G', '아라벨라', '아라벨라'],
    'Truman_Adams': ['H', '트루먼', '애덤스'],
    'Ricky': ['S', '리키', '에어드'],
    'FelixPB': ['S', '펠릭스', '베넷'],
    'W1': ['S', '파시오마티아', '오데트릴'],
    'DarcyIsm': ['G', '다아시', '이즈멜'],
    'TEO928': ['R', '테오도르', '러셀'],
    'Elior': ['R', '엘리오르', '티모테우스'],
    'Eddy_M': ['R', '에셀레드', '무어'],
    'psyche_lin': ['G', '리아트리스', '스노우'],
    'NoraHolloway': ['H', '노라', '할로웨이'],
    '6enjqm1n22': ['H', '벤자민', '로크'],
    'nasaret': ['G', '나샤렛', '브링클리'],
    'Evelyn': ['R', '에블린', '페레즈'],
    'En_L': ['H', '이엔', '레인'],
    'Gray_L': ['S', '리', '그레이'],
    '_RP_00': ['S', '러셀', '패트릭'],
    'jono': ['R', '주노', '바브렉'],
    'EmilyLT': ['H', '에밀리', '로랑'],
    'AG': ['S', '애슈턴', '매버릭'],
    'Isaiah_': ['R', '이사야', '서머스'],
    'Mitch': ['R', '밋치', '린도'],
    '3_lines': ['H', '일', '커스버트슨'],
    'anika': ['G', '아니카', '리']
}