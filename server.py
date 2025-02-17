import os
import http.server
import socketserver
import script

from http import HTTPStatus
from mastodon import Mastodon
from mastodon.streaming import StreamListener


# Create an instance of the Mastodon class
mastodon = Mastodon(
    access_token='roCGE6NPcKrN90zk2Z5rg0-TnDwyuHP7wzH5dJ3qFq4',
    api_base_url='https://strivings.life'
)




class dgListener(StreamListener):
    anwers = ''
    def on_notification(self, notification):
        if notification['type'] == 'mention':
            id = notification['status']['id']
            visibility = notification['status']['visibility']
            if '[바깥일]' in notification['status']['content']:
                answers = '나가려고? 어디로?'
            elif '[집안일]' in notification['status']['content']:
                answers = script.make_daily_script(notification['account']['username'])
            else:
                answers = "무언가 잘못된 것 같다. 다시 시도해 보자. @bunker"
                visibility = 'direct'
        
        mastodon.status_post("@" + notification['account']['username'] + "\n" + 
                            answers, in_reply_to_id = id, 
                            visibility = visibility)

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        # msg = 'Hello! you requested %s' % (self.path)
        mastodon.stream_user(dgListener())
        # self.wfile.write(msg.encode())

port = int(os.getenv('PORT', 80))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)

mastodon.stream_user(dgListener())

httpd.serve_forever()