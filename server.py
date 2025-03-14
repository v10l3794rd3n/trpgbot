import os
import http.server
import socketserver
import script
import re
import mimetypes  # 기본 라이브러리 활용
import time
import threading

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener


# Create an instance of the Mastodon class
mastodon = Mastodon(
    access_token='QkFO1MAAdVPjlBLzgtewEatRfc6KAG2RFGv_9iWfpME',
    api_base_url='https://ellipsishgwt.com'
)


def is_valid_image(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type in ['image/png']

def timeout_function(func, timeout=30, *args, **kwargs):
    """ 특정 함수가 일정 시간 내 실행되지 않으면 강제 종료하는 함수 """
    result = [None]
    
    def wrapper():
        try:
            start_time = time.time()
            result[0] = func(*args, **kwargs)  # API 요청 실행
            end_time = time.time()
            print(f"⏳ 실행 시간: {end_time - start_time:.2f}초")
        except Exception as e:
            result[0] = e  # 예외 저장
    
    thread = threading.Thread(target=wrapper, daemon=True)  
    thread.start()
    thread.join(timeout)  

    if thread.is_alive():  
        print("⚠️ 요청이 너무 오래 걸려 강제 종료합니다.")
        return TimeoutError("⚠️ 요청이 너무 오래 걸려 중단되었습니다.")
    
    return result[0]

def wait_for_media_processing(media_id, timeout=30):
    """업로드된 미디어가 완전히 처리될 때까지 대기"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            media_status = mastodon.media(media_id)
            if media_status['url']:  
                print(f"✅ 미디어 업로드 완료: {media_status['url']}")
                return True  
        except Exception as e:
            print(f"⚠️ 미디어 상태 확인 실패: {e}")
        time.sleep(2)  
    print(f"❌ 미디어 업로드 확인 시간 초과: {media_id}")
    return False

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
                
                # 이미지와 텍스트를 함께 묶어서 하나의 툿에 포함하도록 조정
                image_batch = []
                text_batch = []
                
                for item in results:
                    if os.path.exists(item) and is_valid_image(item):  # 올바른 이미지인지 확인
                        image_batch.append(item)
                    elif isinstance(item, str):  # 텍스트인 경우
                        text_batch.append(item)
                
                formatted_results = []
                while image_batch:
                    formatted_results.append((image_batch[:4], text_batch[:4]))  # 4개씩 묶어서 나누기
                    image_batch = image_batch[4:]
                    text_batch = text_batch[4:]
                
                if text_batch:
                    formatted_results.append(([], text_batch))  # 텍스트를 하나의 툿으로 추가
                
                print(f"📦 정리된 가챠 결과: {formatted_results}")
                
                for image_group, text_group in formatted_results:
                    media_ids = []
                    image_names = []
                    missing_images = []
                    
                    
                    # 이미지 업로드 처리
                    print(f"🖼️ 이미지 업로드 중... {image_group}")
                    for item in image_group:
                        if os.path.exists(item) and is_valid_image(item):  # 올바른 이미지인지 확인
                            result = timeout_function(mastodon.media_post, 30, item)
                            if isinstance(result, Exception):
                                print(f"⚠️ 이미지 업로드 실패: {result}")
                                missing_images.append(os.path.splitext(os.path.basename(item))[0])
                                continue
                            media_id = result['id']

                            if wait_for_media_processing(media_id):  
                                media_ids.append(media_id)
                                image_names.append(os.path.splitext(os.path.basename(item))[0])  
                            else:
                                print(f"❌ 미디어 업로드 확인 실패: {media_id}")
                                missing_images.append(os.path.splitext(os.path.basename(item))[0])
                                continue

                        time.sleep(10)
                        # 툿 작성 (이미지 파일명과 텍스트 출력)

                    status_text = "@" + notification['account']['username'] + "\n"
                    
                    if image_names or text_group:
                        status_text += "\n".join(image_names + text_group)
                    else:
                        status_text += 'ERR:02'

                    if missing_images:
                        status_text += f"\n⚠️ {', '.join(missing_images)}이(가) 나오지 않았어~!"
        
                    
                    print(f"📤 툿 업로드 중... {status_text}")
                    result = timeout_function(mastodon.status_post, 30, status=status_text, media_ids=media_ids if media_ids else None, in_reply_to_id=id, visibility=visibility)
                    if isinstance(result, Exception):
                        print(f"⚠️ 툿 업로드 실패: {result}")
                        continue
                    
                    print("✅ 툿 업로드 완료")
                    time.sleep(5)
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