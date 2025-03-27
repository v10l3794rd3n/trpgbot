import os
import http.server
import socketserver
import script
import re
import time
import threading
import urllib.parse
import random

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener


# Create an instance of the Mastodon class
mastodon = Mastodon(
    access_token='Smv3musvnx_dpoehgY1K9xI76LqDKFU5ojL1L7nd1rA',
    api_base_url='https://ododok.life'
)


def timeout_function(func, timeout=30, *args, **kwargs):
    """ 특정 함수가 일정 시간 내 실행되지 않으면 강제 종료하는 함수 """
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
                if '[피해]' in notification['status']['content']:
                    pattern = r"""
                        \[\s*[^]]*?\s*\]             # 첫 번째 태그 무시 ([피해] 등)
                        \[\s*([^\[\]+\-0-9\s]+)      # 기술명 (예: 단검)
                        \s*([+-]\s*\d+)?\s*\]        # 보정값 (예: -1, +2), 없을 수도 있음
                        (?:\s*\[\s*([^\[\]]+)\s*\])? # 속성 (예: 치명타), 없을 수도 있음
                    """
                    match = re.search(pattern, notification['status']['content'], re.VERBOSE)
                    if match:
                        skill = match.group(1)
                        modifier = match.group(2).replace(" ", "") if match.group(2) else "0"
                        tag = match.group(3) or None
                        answers = script.CoC_damage(user, skill, modifier, tag)
                    else:
                        print("❗ [피해]를 이해하지 못했어.")
                    pass
                else:
                    match = re.search(r"\[\s*([^\[\]+\-\s]+)\s*([+-])\s*(\d+)\s*\]|\[\s*([^\[\]+\-\s]+)\s*\]", notification['status']['content'])
                    if match:
                        skill = match.group(1) or match.group(3)
                        if match.group(2) and match.group(3):
                            modifier = f"{match.group(2)}{match.group(3)}"
                        else:
                            modifier = "0"
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
                        else:
                            answers = script.CoC_skill(id, skill, int(modifier))
                    else:
                        print("❗ [기능]을 이해하지 못했어.")  
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