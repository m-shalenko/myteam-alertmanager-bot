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

3. Also, you must define some variables in your myteam-alertmanager-bot installation.
- Define `API_URL_BASE` or `args.api-url-base` variable (required)
- Define `BOT_NAME` or `args.bot-name` variable (required)
- Define default `CHAT_ID` or `args.chat-id` variable (required)
- Define extra chat ids using the variable like this `CHAT_ID_<alertmanager_receiver_name>`
- Define `API_TOKEN` or `args.api-token` (required)
- Define `args.parse-mode` (optional, default `HTML`)

4. Quick start and test:

```bash
cd app
python3 manager.py

curl localhost:8080/api/v1/push -X POST -d '{"receiver": "test", "status": "resolved", "alerts": [{"status": "firing", "labels": {"alertgroup": "test", "alertname": "test", "instance": "test", "job": "node-exporter", "prometheus": "monitoring-system/vmagent", "severity": "info"}, "annotations": {"instance": "test", "reference": "", "summary": "test", "value": "test"}, "startsAt": "2022-06-29T11:34:26.055376888Z", "endsAt": "0001-01-01T00:00:00Z", "generatorURL": "http://vmalert-vmalert-7b4dc58787-jzfvn:8080/api/v1/10784142485096446030/2135157705199415880/status", "fingerprint": "767a027249c67bd4"}], "groupLabels": {"alertname": "test"}, "commonLabels": {"alertgroup": "test", "alertname": "test", "instance": "test", "job": "node-exporter", "prometheus": "monitoring-system/vmagent", "severity": "info"}, "commonAnnotations": {"instance": "test", "reference": "", "summary": "test", "value": "test"}}' -H 'Content-Type: application/json' -v
```
5. To make it all works using alertmanager, you have to define a `webhook_config` in your alertmanager installation.
```yaml
# /etc/alertmanager/alertmanager.yaml
route:
  receiver: test
  continue: false
  routes:
    - receiver: test
      group_by:
        - alertname
        - group
      matchers:
        - <some_label>="<some_value"
      continue: true
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 1h
receivers:
  - name: test
    webhook_configs:
      - send_resolved: true
        url: <http_myteam_alertmanager_bot_url>/api/v1/push
```
