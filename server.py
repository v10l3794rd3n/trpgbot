import os
import http.server
import socketserver
import script
import re

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener


# Create an instance of the Mastodon class
mastodon = Mastodon(
    access_token='QkFO1MAAdVPjlBLzgtewEatRfc6KAG2RFGv_9iWfpME',
    api_base_url='https://ellipsishgwt.com'
)




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
                result = script.format_results(script.generate_gacha_results())
                
                previous_post = None
                
                for batch in result:
                    media_ids = []
                    text_content = []
                    image_names = []
                    
                    # 이미지 업로드 처리
                    for item in batch:
                        if os.path.exists(item):  # 이미지 파일인 경우
                            media = mastodon.media_post(item)
                            media_ids.append(media['id'])
                            image_names.append(os.path.splitext(os.path.basename(item))[0])  # 확장자 제외 파일명 저장
                        else:  # 텍스트인 경우
                            text_content.append(item)
                    
                    # 툿 작성 (이미지 파일명과 텍스트 출력)
                status_text = "@" + notification['account']['username'] + "\n"
                status_text += "\n".join(image_names + text_content) if image_names or text_content else 'ERR:02'
                
                # 툿 업로드
                post_args = {
                    "status": status_text,
                    "media_ids": media_ids,
                    "in_reply_to_id": previous_post['id'] if previous_post else id,
                    "visibility": visibility
                }
                
                previous_post = mastodon.status_post(**post_args)
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