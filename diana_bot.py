#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import requests
from HTMLParser import HTMLParser
import re
import urllib2
import json
from credentials import BOT_URL, CHANNEL_DIANA, CHANNEL_WW

class InsightsControllerResponseParser(HTMLParser):
    limit = 5
    current = 0
    message = 'This pages on West-Wing wiki need our help :captain:'

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if self.current < self.limit and attr[0] == 'href' and 'insights=wantedpages' in attr[1]:
                m = re.search('.*/wiki/([^?]*)\?action=edit', attr[1])
                title_decoded = urllib2.unquote(m.group(1))
                title_without_spaces = title_decoded.encode('ISO 8859-1')
                title = title_without_spaces.replace('_', ' ')

                self.current+=1
                self.message += '\n\n<' + m.group(0) + '|' + title + '>'

    def getMessage(self):
        print self.message
        return self.message

class WikiaApiController():
    def make_request(self):
        response = requests.get(
                'http://w-w.wikia.com/wikia.php',
                params = {
                    'controller': 'Insights',
                    'method': 'index',
                    'par': 'wantedpages'
                }
            ).text

        return response

class SlackController(object):
    def __init__(self, bot_channel = CHANNEL_DIANA):
        self.bot_channel = bot_channel

    def post_slack_message(self, message):
        data = {
            'channel': self.bot_channel,
            'text': message,
        }

        payload = json.dumps(data)
        response = requests.post(BOT_URL,
                      data = {
                          'payload': payload,
                      })

        print '\nPosting to Slack: done'

if __name__ == "__main__":
    parser = InsightsControllerResponseParser()
    api_connector = WikiaApiController()
    slack_controller = SlackController(CHANNEL_WW)
    
    response = api_connector.make_request()
    parser.feed(response)
    message = parser.getMessage()
    slack_controller.post_slack_message(message)
