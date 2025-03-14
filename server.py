import os
import http.server
import socketserver
import script
import re
import time
import threading
import urllib.parse

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener


# Create an instance of the Mastodon class
mastodon = Mastodon(
    access_token='QkFO1MAAdVPjlBLzgtewEatRfc6KAG2RFGv_9iWfpME',
    api_base_url='https://ellipsishgwt.com'
)



def generate_drive_link(file_id):
    """Google Drive 공유 링크를 Direct Image Link로 변환"""
    return f"https://drive.google.com/uc?export=view&id={file_id}"

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
            visibility = notification['status']['visibility']
            if '[출석]' in notification['status']['content']:
                answers = script.make_script(notification['account']['username'])
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
            elif '[탐색' in notification['status']['content']:
                s = re.search(r"탐색/(.*?)\]", notification['status']['content']).group(1)
                #s = [int(s) for s in re.findall(r"-?\d+\.?\d*", notification['status']['content'])]
                answers = script.make_farming_script(notification['account']['username'], s)
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
            elif '[상점' in notification['status']['content']:
                s = re.search(r"상점/(.*?)\]", notification['status']['content']).group(1)
                answers = script.make_store_script(notification['account']['username'], s)
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
            elif '[랜덤박스' in notification['status']['content'] or '[랜덤 박스' in notification['status']['content']:
                s = [int(s) for s in re.findall(r"-?\d+\.?\d*", notification['status']['content'])]
                answers = script.make_gacha_script(s[0])
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
            elif '[인벤토리' in notification['status']['content']:
                s = re.search(r"인벤토리/(.*?)\]", notification['status']['content']).group(1)
                answers = script.make_inventory_script(s)
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
            elif '[마법약' in notification['status']['content']:
                s = re.search(r'\[.*?/([^/\]]+)/.*?\]', notification['status']['content']).group(1)
                potion = re.search(r'\[.*?/(.*?)/([^/\]]+)\]', notification['status']['content']).group(2)
                answers = script.make_potion_script(s, potion)
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
            elif '[프롬]' in notification['status']['content']:
                print("🔍 가챠 결과 생성 중...")
                results = script.generate_gacha_results()
                print(f"🎲 가챠 결과: {results}")
                
                # 가챠 결과에서 텍스트와 이미지 분리
                text_results = [r for r in results if isinstance(r, str) and not r.startswith("http")]  # 텍스트만 분리
                image_links = [(r, os.path.splitext(os.path.basename(urllib.parse.unquote(r)))[0]) for r in results if isinstance(r, str) and r.startswith("http")]  # (이미지 URL, 한글 파일명 복원)
    
                print(f"📦 정리된 가챠 이미지 링크: {image_links}")
                print(f"📝 정리된 가챠 텍스트 결과: {text_results}")

                """가챠 결과(이미지와 텍스트)를 여러 개의 툿으로 나눠서 올리기"""
                previous_post = None
                max_links_per_post = 4
                
                # 텍스트 결과 먼저 툿에 올리기
                if text_results:
                    text_post = f"상자를 열면......\n" + "\n".join(text_results)
                    if notification:
                        text_post = f"@{notification['account']['username']}\n" + text_post
                    
                    result = timeout_function(
                        mastodon.status_post, 30,
                        status=text_post,
                        in_reply_to_id=previous_post['id'] if previous_post else id,
                        visibility=visibility
                    )
                    
                    if isinstance(result, Exception):
                        print(f"⚠️ 텍스트 툿 업로드 실패: {result}")
                    else:
                        previous_post = result
                        print(f"✅ 텍스트 툿 업로드 완료: {previous_post}")
                    
                    time.sleep(3)
                
                # 이미지 링크 툿 나눠서 올리기 (파일명 포함)
                for i in range(0, len(image_links), max_links_per_post):
                    post_text = "물건을 가져가자!\n"
                    for link, filename in image_links[i:i+max_links_per_post]:
                        decoded_filename = urllib.parse.unquote(filename)  # 한글 파일명 복원
                        post_text += f"{decoded_filename}: {link}\n"
                    
                    if notification:
                        post_text = f"@{notification['account']['username']}\n" + post_text
                    
                    result = timeout_function(
                        mastodon.status_post, 30,
                        status=post_text,
                        in_reply_to_id=previous_post['id'] if previous_post else None,
                        visibility=visibility
                    )
                    
                    if isinstance(result, Exception):
                        print(f"⚠️ 이미지 툿 업로드 실패: {result}")
                        continue
                    
                    previous_post = result  # 이전 툿을 스레드로 연결
                    print(f"✅ 이미지 툿 업로드 완료: {previous_post}")
                    time.sleep(3)

            else:
                pass
        
        

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