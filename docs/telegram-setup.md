# Telegram Bot Setup

## 1. Create a Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts to name your bot
4. Copy the **bot token** (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## 2. Get Your Chat ID

1. Send a message to your new bot
2. Open in browser: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `"chat":{"id": <YOUR_CHAT_ID>}` in the response

## 3. Configure .env

```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=987654321
```

## 4. Test

After starting the CRM, the bot will send you a notification when a prospect opens an email.
