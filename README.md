# telegrambot
my telegram bot. initial purpose is for "good morning" memes, but ig ill use it for other stuff eventually

## some info before we start
this code is in a bigger directory which I prefer not putting here, since it contains a lot of other
crap, as well as private stuff like the bot token.
it is built as follows:
```
>bot
->src (this repo)
->videos
->token.key
```

## todo

* proper context menu for managing the video directory (deleting etc) - (/manage_vids)
* set video for next day's daily meme, instead of sending random meme (/this_meme)
* IN SERVER manage periodic cron to automatically pull master branch!! (maybe even make /update_bot for self update?)
