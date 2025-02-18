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
            elif '[비행' in notification['status']['content']:
                s = [int(s) for s in re.findall(r"-?\d+\.?\d*", notification['status']['content'])]
                answers = script.make_flight_script(notification['account']['username'], s[0])
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
            elif '[마법' in notification['status']['content']:
                s = re.search(r"마법/(.*?)\]", notification['status']['content']).group(1)
                answers = script.make_magic_script(notification['account']['username'], s)
                mastodon.status_post("@" + notification['account']['username'] + "  " + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)
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