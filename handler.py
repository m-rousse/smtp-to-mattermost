import json
import os
import re
import yaml

import requests
from aiosmtpd.handlers import Message


class MessageHandler(Message):
    def __init__(self, *args, **kargs):
        Message.__init__(self, *args, **kargs)

        config = os.getenv('CONFIG', '/etc/smtp-to-mattermost/config.yml')
        print(config)
        if not os.path.exists(config):
            print('Config doesn\'t exists!')
            exit(1)

        self.config = yaml.safe_load(open(config))


    def handle_message(self, message):
        """ This method will be called by aiosmtpd server when new mail will
            arrived.
        """
        print('message received', message)
        options = self.process_rules(message)

        print('matched', options)
        self.send_to_mattermost(self.extract_text(message), **options)

        if options['debug']:
            self.send_to_mattermost('DEBUG: ' + str(message), **options)

    def process_rules(self, message):
        """ Check every rule from config and returns options from matched
        """
        default = self.config['default']

        fields = {
            'from': message['From'],
            'to': message['To'],
            'subject': message['Subject'],
            'body': message.get_payload()
        }

        print(fields)

        for rule in self.config['rules']:
            # TODO: better handling of None values than just str(value)
            tests = (
                re.match(rule[field], str(value))
                for field, value in fields.items() if field in rule
            )

            if all(tests):
                options = default.copy()
                options.update(rule['options'])
                return options

        return default

    def extract_text(self, message):
        fmt = self.config['default'].get('format', '%(body)s')
        body = message.get_payload()
        subject = message['Subject']
        return fmt % dict(body=body, subject=subject)

    def send_to_mattermost(self, text, **options):
        print('sending to mattermost', text, options)

        url = options["mattermost_webhook"]
        payload = {
            'channel' : options['channel'],
            'username' : options['username'],
            'text' : text,
        }

        if 'icon_url' in options:
            payload['icon_url'] = options['icon_url']
        elif 'icon_emoji' in options:
            payload['icon_emoji'] = options['icon_emoji']

        requests.post(url, data=json.dumps(payload))
