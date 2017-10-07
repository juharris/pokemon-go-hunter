import logging
import re
import time

import twitter
from pushbullet import Pushbullet

_twitter_api = twitter.Api(consumer_key='TODO',
                           consumer_secret='TODO',
                           access_token_key='TODO',
                           access_token_secret='TODO')

_pb = Pushbullet(api_key='TODO',
                 encryption_password='TODO')

devices = _pb.devices
_device = None
for d in devices:
    if d.nickname == "TODO":
        _device = d
assert _device is not None, "Couldn't find Pushbullet device."


def main(screen_name: str,
         pattern,
         callback,
         period_s: int = 61):
    logging.info("Waiting for tweets.")
    since_id = None
    while True:
        statuses = _twitter_api.GetUserTimeline(screen_name=screen_name,
                                                since_id=since_id,
                                                trim_user=True)
        for status in statuses:
            if since_id is None:
                since_id = status.id
            else:
                since_id = max(since_id, status.id)

            text = status.text
            m = pattern.search(text)
            if m:
                callback(status)

        time.sleep(period_s)


def notify(status):
    text = status.text
    for url in status.urls:
        text = text.replace(url.url, url.expanded_url)
    logging.info("Sending: \"%s\".", text)
    _pb.push_sms(_device, 'TODO', text)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(name)s:%(filename)s:%(funcName)s\n%(message)s',
                        level=logging.INFO)
    # Example.
    main(screen_name='montrealpokemap',
         pattern=re.compile(r'\b(Unown)\b', re.IGNORECASE),
         callback=notify)
