# Tutorial 4: Building Discord Bots natively

You don't need a massive library to build quick Chat Bots or webhook interceptors! EPL has `http_post` builtin to make remote server interactions incredibly simple.

## Step 1: The Request

Simply package your payload as an EPL Map, serialize it using `json_stringify`, and specify your HTTP headers!

```epl
Function send_discord_message takes channel_id, content
    url = "https://discord.com/api/v10/channels/" + channel_id + "/messages"
    payload = Map with content = content
    headers = ["Authorization: Bot YOUR_BOT_TOKEN", "Content-Type: application/json"]
    
    response = http_post(url, json_stringify(payload), headers)
    Return response
End
```

## Step 2: Setting up the Webhook Listener

Discord natively supports pushing events to an endpoint via Webhooks. Build a lightning-fast Webhook server in EPL! 

```epl
Create WebApp called discordWebhook

Route "/api/interactions" responds with
    event_data = request.body_json
    
    If event_data.get("type") == 1 Then
        Note: Discord Ping Event checking if server is alive!
        Send json Map with type = 1
    Otherwise
        message_content = event_data.get("content")
        
        Note: Run arbitrary chat interactions
        If message_content == "!ping" Then
            send_discord_message(channel_id, "Pong! Built with EPL 🚀")
        End
    End
End

Start discordWebhook on port 8000
```
