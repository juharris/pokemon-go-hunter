import logging
import os
import re
import time

import twitter
import yaml
from pushbullet import Pushbullet


def get_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.yaml')
    with open(config_path) as f:
        return yaml.load(f)


def get_twitter_api(config):
    api_config = config['API']
    twitter_api_config = api_config['Twitter']
    return twitter.Api(consumer_key=twitter_api_config['consumer key'],
                       consumer_secret=twitter_api_config['consumer secret'],
                       access_token_key=twitter_api_config['access token key'],
                       access_token_secret=twitter_api_config['access token secret'])


def get_pushbullet_api(config):
    api_config = config['API']
    pushbullet_api_config = api_config['Pushbullet']
    return Pushbullet(api_key=pushbullet_api_config['api key'],
                      encryption_password=pushbullet_api_config['encryption password'])


def get_pushbullet_device(pb, config):
    devices = pb.devices
    result = None
    for d in devices:
        if d.nickname == config['API']['Pushbullet']['device name']:
            result = d
    assert result is not None, "Couldn't find Pushbullet device."
    return result


_config = get_config()
_twitter_api = get_twitter_api(_config)
_pb = get_pushbullet_api(_config)
_device = get_pushbullet_device(_pb, _config)


def main(screen_name: str,
         pattern,
         callback,
         period_s: int = 61):
    logging.info("Waiting for tweets.")
    since_id = None
    while True:
        try:
            statuses = _twitter_api.GetUserTimeline(screen_name=screen_name,
                                                    since_id=since_id,
                                                    trim_user=True)
        except:
            logging.exception("Error getting tweets.")
            time.sleep(period_s / 4)
            continue

        for status in statuses:
            if since_id is None:
                since_id = status.id
            else:
                since_id = max(since_id, status.id)

            text = status.text
            m = pattern.search(text)
            logging.debug(text)
            if m:
                try:
                    callback(status)
                except:
                    logging.exception("Callback failed.")

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
    # TODO Read from config.
    # Example.
    main(screen_name='montrealpokemap',
         pattern=re.compile(r'\b(Unown)\b', re.IGNORECASE),
         callback=notify)
