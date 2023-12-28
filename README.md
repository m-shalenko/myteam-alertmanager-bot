# MyTeam Alertmanager Bot

- [MyTeam Bot API](https://myteam.mail.ru/botapi/tutorial/)
- [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/)

This is a bot that can be integrated with [VKTeams Messenger](https://teams.vk.com/) and [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/)

### How to install

1. First of all, you have to create a bot in MyTeam (VK Teams) messenger via Metabot. Metabot is a father of the all bots like the @BotFather in the Telegram messenger.
- Type "Metabot" in the search bar and choose a chat
- Press "start"
- Type `/newbot` to create a new bot
- Enter an unique bot nick. It must end with a "bot"
- Save an api token

2. Secondly, you have to allow bot to join chats.
- Choose "Metabot" chat
- Type `/setjoingroups` and enter botId or nick name of bot

3. Also, you must define some environment variables in your myteam-alertmanager-bot installation.
- Define `API_URL_BASE` variable (required)
- Define `BOT_NAME` variable (required)
- Define default `CHAT_ID` variable (required)
- If you would like to use a few chats to send alerts, define extra chat ids using the variable like this one `CHAT_ID_<ALERTMANAGER_RECEIVER_NAME>`. `<ALERTMANAGER_RECEIVER_NAME>` must match receiver name in your alertmanager config and be upper-case, `-` replaced with `_`.
- Define `API_TOKEN` variable (required)

4. Quick start and test:

```bash
export API_URL_BASE="https://api.vkteams.example.com/bot/v1/"
export BOT_NAME="<bot_name>"
export API_TOKEN="<bot_token>"
export CHAT_ID="<default_chat_id>"
export CHAT_ID_VKTEAMS_FOO_ALERTS="<chat_id_1>"
export CHAT_ID_VKTEAMS_BAR_ALERTS="<chat_id_2>"
cd app/
python3 manager.py

curl localhost:8080/api/v1/push -X POST -d '{"receiver": "vkteams-foo-alerts", "status": "firing", "alerts": [{"status": "firing", "labels": {"alertgroup": "test", "alertname": "test", "instance": "test", "job": "node-exporter", "prometheus": "monitoring-system/vmagent", "severity": "info"}, "annotations": {"instance": "test", "reference": "", "summary": "test", "value": "test"}, "startsAt": "2022-06-29T11:34:26.055376888Z", "endsAt": "0001-01-01T00:00:00Z", "generatorURL": "http://vmalert-vmalert-7b4dc58787-jzfvn:8080/api/v1/10784142485096446030/2135157705199415880/status", "fingerprint": "767a027249c67bd4"}], "groupLabels": {"alertname": "test"}, "commonLabels": {"alertgroup": "test", "alertname": "test", "instance": "test", "job": "node-exporter", "prometheus": "monitoring-system/vmagent", "severity": "info"}, "commonAnnotations": {"instance": "test", "reference": "", "summary": "test", "value": "test"}}' -H 'Content-Type: application/json' -v
```
5. To make it all works using alertmanager, you have to define a `webhook_config` in your alertmanager installation.
```yaml
# alertmanager example config
global:
  resolve_timeout: 5m
  http_config:
    follow_redirects: true
    enable_http2: true
  smtp_hello: localhost
  smtp_require_tls: true
  pagerduty_url: https://events.pagerduty.com/v2/enqueue
  opsgenie_api_url: https://api.opsgenie.com/
  wechat_api_url: https://qyapi.weixin.qq.com/cgi-bin/
  victorops_api_url: https://alert.victorops.com/integrations/generic/20131114/alert/
  telegram_api_url: https://api.telegram.org
  webex_api_url: https://webexapis.com/v1/messages
route:
  receiver: vkteams-foo-alerts
  continue: false
  routes:
    - receiver: vkteams-foo-alerts
      group_by:
        - alertname
        - group
      matchers:
        - team="FOO"
      continue: true
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
    - receiver: vkteams-bar-alerts
      group_by:
        - alertname
        - group
      matchers:
        - team="BAR"
      continue: true
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
receivers:
  - name: vkteams-foo-alerts
    webhook_configs:
      - send_resolved: true
        http_config:
          follow_redirects: true
          enable_http2: true
        url: http://myteam-alertmanager-bot.example.com:8080/api/v1/push
        max_alerts: 0
  - name: vkteams-bar-alerts
    webhook_configs:
      - send_resolved: true
        http_config:
          follow_redirects: true
          enable_http2: true
        url: http://myteam-alertmanager-bot.example.com:8080/api/v1/push
        max_alerts: 0
templates:
  - /etc/vm/configs/**/*.tmpl
```
