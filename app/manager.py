#!/usr/bin/env python3

import os
import sys
import json
import logging
import jsonschema
from aiohttp import web
from bot.bot import Bot
from jinja2 import Template
from traceback import format_exc
from argparse import ArgumentParser
from pythonjsonlogger import jsonlogger

def set_log_level(level):
    if level == 'INFO' or level == 'info':
      log_level = logging.INFO
    elif level == 'DEBUG' or level == 'debug':
      log_level = logging.DEBUG
    elif level == 'ERROR' or level == 'error':
      log_level = logging.ERROR
    else:
      log_level = logging.INFO
    return log_level

def create_alert_msg(message):
    with open('templates/alert_template.j2') as f:
      base = f.read()
    t = Template(base)
    alert_msg = t.render(
      status=message['status'],
      common_labels=message['commonLabels'],
      common_annotations=message['commonAnnotations'],
      alerts=message['alerts']
    )
    return alert_msg

def validate_jsonschema(instance, schema):
    try:
      jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
      return False
    return True

async def push_alert(request):
    schema = {
      "type": "object",
      "required": ["status", "receiver"],
      "properties": {
        "version": {"type": "string"},
        "groupKey": {"type": "string"},
        "truncatedAlerts": {"type": "number"},
        "status": {"type": "string"},
        "receiver": {"type": "string"},
        "groupLabels": {"type": "object"},
        "commonLabels": {"type": "object"},
        "commonAnnotations": {"type": "object"},
        "externalURL": {"type": "string"},
        "alerts": {
          "type": "array",
          "minItems": 1,
          "contains": {
            "type": "object",
            "properties": {
              "status": {"type": "string"},
              "labels": {"type": "object"},
              "annotations": {"type": "object"},
              "startsAt": {"type": "string"},
              "endsAt": {"type": "string"},
              "generatorURL": {"type": "string"},
              "fingerprint": {"type": "string"}
            }
          },
        },
      },
    }
    try:
      json_request = await request.json()
      validate_json = validate_jsonschema(json_request, schema)

      if validate_json:
        msg = 'JSON validation was successful'
        logger.info(msg, extra={'alert': json_request})

        try:
          alert_msg = create_alert_msg(json_request)

          chat_receiver = json_request["receiver"].upper()
          chat_receiver = chat_receiver.replace("-","_")

          chat_id = os.getenv("CHAT_ID_" + chat_receiver, envs['chat_id'])

          send_message = bot.send_text(chat_id=chat_id, parse_mode=envs['parse_mode'], text=alert_msg)
          status = send_message.status_code

          try:
            if status == 200:
              msg = 'Message successfully sent'
              json_response = {'status': 'success'}
              logger.info(msg)
              return web.json_response(json_response, status=status, content_type='application/json')

            elif status == 404:
              msg = f"{envs['api_url_base']} is bad api endpoint"
              json_response = {'status': 'failed', 'message': msg}
              logger.error(msg)
              return web.json_response(json_response, status=status, content_type='application/json')

            else:
              msg = f'HTTP status code is {status}'
              json_response = {'status': 'failed', 'message': 'Unknown error'}
              logger.error(msg)
              return web.json_response(json_response, status=status, content_type='application/json')

          except web.HTTPException:
            logger.error(format_exc())

        except Exception:
          status = 500
          json_response = {'status': 'failed', 'message': format_exc()}
          logger.error(format_exc())
          return web.json_response(json_response, status=status, content_type='application/json')

      else:
        status = 400
        msg = 'Invalid JSON schema'
        json_response = {'status': 'failed', 'message': msg}
        logger.error(msg)
        return web.json_response(json_response, status=status, content_type='application/json')

    except json.decoder.JSONDecodeError:
      status = 400
      json_response = {'status': 'failed', 'message': format_exc()}
      logger.error(format_exc())
      return web.json_response(json_response, status=status, content_type='application/json')

async def healthcheck(request):
    try:
      json_response = {'status': 'success', 'message': 'healthcheck passed'}
      return web.json_response(json_response)
    except web.HTTPException:
      logger.error(format_exc())
      sys.exit(1)

parser = ArgumentParser()
parser.add_argument("--log-level", type=str, help='specify a log level')
parser.add_argument("--api-url-base", type=str, help="specify an api endpoint")
parser.add_argument("--api-token", type=str, help="specify an api token")
parser.add_argument("--bot-name", type=str, help="specify a bot name")
parser.add_argument("--chat-id", type=str, help="specify a nick, stamp or chat_id")
parser.add_argument("--parse-mode", type=str, help="specify a text format")
args = parser.parse_args()

envs = {
  "log_level": os.getenv('LOG_LEVEL', args.log_level),
  "api_url_base": os.getenv('API_URL_BASE', args.api_url_base),
  "api_token": os.getenv('API_TOKEN', args.api_token),
  "bot_name": os.getenv('BOT_NAME', args.bot_name),
  "chat_id": os.getenv('CHAT_ID', args.chat_id),
  "parse_mode": args.parse_mode or "HTML"
}

log_level = set_log_level(envs['log_level'])
logger = logging.getLogger()
logger.setLevel(log_level)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(levelname)%(asctime)%(message)%(pathname)%(lineno))')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

for key, value in envs.items():
  if value is None and key != 'log_level':
    msg = f'{key.upper()} is not defined'
    logger.error(msg)
    sys.exit(1)

bot = Bot(api_url_base=envs['api_url_base'], name=envs['bot_name'], token=envs['api_token'], is_myteam=True)

app = web.Application()
app.add_routes([
    web.post('/api/v1/push', push_alert),
    web.get('/health', healthcheck)
  ])

if __name__ == '__main__':
    web.run_app(app)
