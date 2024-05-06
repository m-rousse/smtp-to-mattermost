# SMTP to Mattermost

SMTP to Mattermost is simple email-to-mattermost gateway. It support basic rules for routing
messages to different mattermost channels from different bots.

Main purpose of SMTP to Mattermost is to redirect messages from old-school systems which doesn't
support messaging other than email. For example cron and monit
(https://mmonit.com/monit/) support only emails as the only system for
notifications.

This project is heavily inspired on https://github.com/ont/slacker which does the same gateway
with Slack instead of Mattermost. Most of the credit goes [@ont](https://github.com/ont).

## Installation

SMTP to Mattermost can be easily installed via docker:

```bash
docker pull mrousse/smtp-to-mattermost
```

Then run container with custom `config.yml`:

```bash
docker run \
    -d --restart=always \
    --name=smtp-to-mattermost \
    -v /path/to/config.yml:/etc/smtp-to-mattermost/config.yml \
    -p localhost:8025:8025 \
    mrousse/smtp-to-mattermost
```
Last command will start SMTP server on `localhost:8025`

## Config

SMTP to Mattermost supports simple list of rules for configuring target mattermost channel, bot
name and its avatar depending on email content.

There are two sections:
  * default: this is default options for sending message to mattermost.
  * rules: list of rules for matching email message against 'from', 'to' and/or 'subject'.

Each rule in list tested in order. First matched rule is used to update
options values from 'default' section of config.

Example `config.yml` for redirecting email to two channels: `#monit` and `#cron`:
```yaml
# default values for channel, bot name, avatar url, mattermost token and debug mode
default:
    channel: 'general'
    username: smtp-to-mattermost
    icon_url: ''
    mattermost_webhook: "https://mattermost.server.local/hooks/aaaaaaaaaaaaaaaaaaaaaaaaaa"
    debug: false
    format: "subject: %(subject)s; body: %(body)s"  ## default mattermost message format


# list of rules
rules:
    - name: Monit rule
      from: monit@.*

      options:
          username: monit
          channel: 'monitoring'
          icon_url: 'https://bitbucket.org/tildeslash/monit/avatar/128'
          debug: false


    - name: Cron rule
      from: root@localhost
      subject: Cron.*  ## cron email subject starts with "Cron..."

      options:
          username: cron
          channel: 'cron'
          icon_url: ''
          debug: true  ## will output full email with all headers
```
