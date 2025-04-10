import os
import http.server
import socketserver
import script
import re
import time
import threading
import random

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener
from collections import namedtuple


# Create an instance of the Mastodon class
mastodon = Mastodon(
    access_token='RqbtBP8gWi4dHA3A_VRaXJj9JDKuclipanDGIDI1Uf4',
    api_base_url='https://violetgarden.pe.kr'
)


# 예비용 함수 (실제로 쓰이지 않음)

def timeout_function(func, timeout=30, *args, **kwargs):
    result = [None]
    
    def wrapper():
        try:
            start_time = time.time()
            result[0] = func(*args, **kwargs)
            end_time = time.time()
            print(f"⏳ 실행 시간: {end_time - start_time:.2f}초")
        except Exception as e:
            result[0] = e
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        print("⚠️ 요청이 너무 오래 걸려 강제 종료합니다.")
        return TimeoutError("⚠️ 요청이 너무 오래 걸려 중단되었습니다.")
    
    return result[0]




class dgListener(StreamListener):
    def on_notification(self, notification):
        print('on_notification')
        if notification['type'] == 'mention':
            print('mention')
            id = notification['status']['id']
            user = notification['account']['username']
            visibility = notification['status']['visibility']
            if '[CoC]' in notification['status']['content']:
                if '[광기]' in notification['status']['content']:                
                    if '[실시간]' in notification['status']['content']:
                        answers = script.CoC_insane_now()
                    elif '[요약]' in notification['status']['content']:
                        answers = script.CoC_insane_summary()
                elif '[피해]' in notification['status']['content']:
                    matches = re.findall(r"\[\s*([^\[\]]+?)\s*\]", notification['status']['content'])

                    if len(matches) >= 3:
                        skill_raw = matches[2]
                        skill_match = re.match(r"([^\+\-\s]+)\s*([+-]\s*\d+)?", skill_raw)
                        if skill_match:
                            skill = skill_match.group(1)  # → '글록17'
                            modifier = skill_match.group(2).replace(" ", "") if skill_match.group(2) else "0"
                        else:
                            skill = skill_raw.strip()
                            modifier = "0"

                        tag = matches[3].strip() if len(matches) >= 4 else None
                        answers = script.CoC_damage(user, skill, int(modifier), tag)
                    else:
                        print("❗ [피해]를 이해하지 못했어.")
                    pass
                else:
                    tags = re.findall(r"\[\s*([^\[\]+\-]+?)\s*(?:([+-])\s*(\d+))?\s*\]", notification['status']['content'])
                    if len(tags) >= 2:
                        skill = tags[1][0]  # 두 번째 태그의 기술명
                        modifier = f"{tags[1][1]}{tags[1][2]}" if tags[1][1] and tags[1][2] else "0"
                        print("skill:", skill)
                        print("modifier:", modifier)
                        stat = ['근력', '건강', '크기', '민첩', '외모', '지능', '정신', '교육']
                        if skill in stat:
                            answers = script.CoC_stat(user, skill, int(modifier))
                        elif skill == '이성':
                            # 1. 계정 정보 가져오기
                            account = mastodon.account(notification['account']['id'])
                            # 2. 부가 필드 중 "SAN" 찾기
                            for field in account.get('fields', []):
                                if field.get('name', '').strip().upper() == 'SAN':
                                    raw_value = field.get('value', '')
                                    # HTML 태그 제거
                                    text = re.sub(r'<.*?>', '', raw_value)
                                    # 숫자 추출
                                    match = re.search(r'\d+', text)
                                    if match:
                                        sanity = int(match.group())
                            answers = script.CoC_sanity(sanity, int(modifier))
                        elif skill == '행운':
                            # 1. 계정 정보 가져오기
                            account = mastodon.account(notification['account']['id'])
                            # 2. 부가 필드 중 "LUCK" 찾기
                            for field in account.get('fields', []):
                                if field.get('name', '').strip().upper() == 'LUCK':
                                    raw_value = field.get('value', '')
                                    # HTML 태그 제거
                                    text = re.sub(r'<.*?>', '', raw_value)
                                    # 숫자 추출
                                    match = re.search(r'\d+', text)
                                    if match:
                                        sanity = int(match.group())
                            answers = script.CoC_sanity(sanity, int(modifier))
                        else:
                            answers = script.CoC_skill(user, skill, int(modifier))
                    else:
                        print("❗ [기능]을 이해하지 못했어.")  
            elif '[인세인]' in notification['status']['content']:
                if '분야' in notification['status']['content']:
                    match = re.search(r"\[인세인\]\[\s*분야\s*/\s*([^\[\]/]+)\s*\]", notification['status']['content'])
                    if match:
                        category = match.group(1)
                        answers = script.insane_category(user, category)
                elif '[광기카드등록]' in notification['status']['content']:
                    AccountField = namedtuple("AccountField", ["name", "value"])
                    cards = str(script.inSANe_insert_card())
                    me = mastodon.account_verify_credentials()
                    fields = me.get('fields', [])
                    fields_data = []
                    found = False
                    for field in fields:
                        name = getattr(field, 'name', '').strip()
                        value = getattr(field, 'value', '')
                        if name.upper() == 'CARD':
                            value = cards
                            found = True
                        fields_data.append(AccountField(name=name, value=value))
                    if not found and len(fields_data) < 4:
                        fields_data.append(AccountField(name='CARD', value=cards))
                    mastodon.account_update_credentials(fields=fields_data)
                    answers = "✅ 광기카드가 등록되었습니다."
                elif '[광기카드]' in notification['status']['content']:
                    AccountField = namedtuple("AccountField", ["name", "value"])
                    me = mastodon.account_verify_credentials()
                    fields_data = [{'name': f.name, 'value': f.value} for f in me.get('fields', [])]
                    insane_index = None
                    insane_count = None
                    for i, field in enumerate(fields_data):
                        if field.get('name', '').strip().upper() == 'CARD':
                            try:
                                insane_count = int(str(field.get('value', '')).strip())
                                insane_index = i
                            except ValueError:
                                print("정수 아님")
                            break
                    answers = script.inSANe_card(insane_count)
                    if insane_index is not None and insane_count is not None:
                        new_count = insane_count - 1
                        fields_data[insane_index]['value'] = str(new_count)
                        converted_fields = [AccountField(name=f['name'], value=f['value']) for f in fields_data]
                        mastodon.account_update_credentials(fields=converted_fields)
                    visibility = 'direct'
                else:
                    account = mastodon.account(notification['account']['id'])
                    fears = []
                    for field in account.get('fields', []):
                        if field.get('name', '').strip().upper() == 'FEAR':
                            raw_value = field.get('value', '')
                            text = re.sub(r'<.*?>', '', raw_value)
                            fears = [f.strip() for f in text.split(',') if f.strip()]
                            break 
                    tags = re.findall(r"\[\s*([^\[\]]*)\s*\]", notification['status']['content'])
                    skill, modifier, ability = None, "0", None
                    if len(tags) >= 2:
                        raw_skill = tags[1].strip()
                        skill_match = re.match(r"([^\+\-\s]+)?\s*([+-]\s*\d+)?", raw_skill)
                        skill = skill_match.group(1) if skill_match and skill_match.group(1) else None
                        modifier = skill_match.group(2).replace(" ", "") if skill_match and skill_match.group(2) else "0"
                    if len(tags) >= 3:
                        ability = tags[2].strip()
                    answers = script.inSANe_default(user, skill, modifier, ability, fears)
                
############################################## 기타 다이스 #######################################
            elif "[choice" in notification['status']['content']:
                match = re.search(r"\[choice\((.*?)\)\]", notification['status']['content'])
                if match:
                    options = match.group(1).split('/')
                    result = random.choice([opt.strip() for opt in options])
                    answers = f"🔀 {result}"
            else:
                match = re.search(r"\[([^\[\]]+)\]", notification['status']['content'])
                if match:
                    dice_expr = match.group(1)
                    if dice_expr == 'd66':
                        answers = script.m_d66()
                    else:
                        r, max_r, rolls = script.roll_dice_expression(dice_expr)
                        answers = f"🎲 {dice_expr} = {rolls} → {r}"
            
            mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
        
        

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        # msg = 'Hello! you requested %s' % (self.path)
        mastodon.stream_user(dgListener())
        print('get')
        # self.wfile.write(msg.encode())

port = int(os.getenv('PORT', 8080))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)

mastodon.stream_user(dgListener())

httpd.serve_forever()