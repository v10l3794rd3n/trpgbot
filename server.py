import os
import http.server
import socketserver
import script
import re
import mimetypes  # 기본 라이브러리 활용

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
                results = script.generate_gacha_results()
                
                # 이미지와 텍스트를 함께 묶어서 하나의 툿에 포함하도록 조정
                image_batch = []
                text_content = []
                
                for item in results:
                    if os.path.exists(item) and is_valid_image(item):  # 올바른 이미지인지 확인
                        image_batch.append(item)
                    elif isinstance(item, str):  # 텍스트인 경우
                        text_content.append(item)
                
                formatted_results = []
                while image_batch:
                    formatted_results.append(image_batch[:4])  # 4개씩 묶어서 나누기
                    image_batch = image_batch[4:]
                
                if text_content:
                    formatted_results.append(text_content)  # 텍스트를 하나의 툿으로 추가
                
                for batch in formatted_results:
                    media_ids = []
                    image_names = []
                    batch_text_content = []  # 중복 방지용 텍스트 리스트
                    
                    # 이미지 업로드 처리
                    for item in batch:
                        if os.path.exists(item) and is_valid_image(item):  # 올바른 이미지인지 확인
                            try:
                                media = mastodon.media_post(item)
                                media_ids.append(media['id'])
                                image_names.append(os.path.splitext(os.path.basename(item))[0])  # 확장자 제외 파일명 저장
                            except Exception as e:
                                print(f"⚠️ 이미지 업로드 오류: {e}")  # 오류 발생 시 출력하고 해당 이미지 제외
                        else:
                            batch_text_content.append(item)  # 해당 배치에 속한 텍스트만 저장
                    
                    # 툿 작성 (이미지 파일명과 텍스트 출력)
                    status_text = "@" + notification['account']['username'] + "\n"
                    
                    if image_names or batch_text_content:
                        status_text += "\n".join(image_names + batch_text_content)
                    else:
                        status_text += 'ERR:02'
                    
                    mastodon.status_post(status_text, in_reply_to_id=id, visibility=visibility, media_ids=media_ids)
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