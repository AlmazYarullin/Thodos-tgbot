# Thodos

## About
Тодос - телеграм бот, способный запоминать

You can create your own bot for your discord server with using instructions below or add existing one by clicking on link:
https://discord.com/oauth2/authorize?client_id=765299001356058624&permissions=8&scope=bot

## Setup
### Installation
1. Clone repo with using `git clone https://gitlab.com/lllumineux/jobs-97-bot.git`
2. Use `pip install -r requirements.txt` to install dependencies
### Configuration
You have to create `.env` file in the root of the project and put there your tokens as shown in the example below:
```
DISCORD_TOKEN= *discord bot api token*
DISCORD_CLIENT_ID= *discord bot client id*
DISCORD_PERMISSIONS= *discord bot permission number*
DISCORD_SCOPE= *discord bot scope attribute*

DB_NAME= *mongoDB db name*
DB_USER_NAME= *mongoDB db user name*
DB_USER_PASSWORD= *mongoDB db user password*
```
Also, you can change bot's command prefix, messages color, channels names, etc. in *config.py*
### Launching
1. Write `python -m jobs_97_bot` command from the root of the repository to run the bot

## Game process
### General concept of the game
The game is intended to recreate the atmosphere that reigned in the late 90s at Apple, when Steve Jobs returned there, previously exiled for not doing his job well. The players are members of the board of directors, in whose hands the fate of the whole company.

At the beginning of the game, each player gets a role: a supporter of Steve Jobs, his opponent or Steve Jobs himself. There are always more opponents, but they do not know which player is who. On the contrary, there are fewer supporters, but they are familiar both with each other and with Steve Jobs (he is with them too).

The only way for opponents to win is to collect 5 cards in their piggy bank, while supporters have two options to win: they can either collect 6 cards, or put Steve Jobs in the post of CEO, having typed at least 3 cards.

<img alt="Card combination example" src="/jobs_97_bot/img/card_combinations/oos.png" width="300">

### Objectives of the game
Opponents must find out who belongs to which team and prevent supporters from winning. In turn, the goal of the supporters is to win, outwitting the opponents and not allowing themselves to be declassified.

### Game progress
The whole game consists of rounds, divided into two main stages:

First, the vice president, whose position is transferred to the players in turn, nominates a candidate for the post of CEO. If the majority of players agree with the candidacy, the proposed player takes the position. If not, the round starts over, and the VP is transferred to the next player.

If the elections were successful, a set of three cards appears in the vice president's personal messages. He is asked to exclude one of them, thereby leaving only two in the set. The remaining cards are sent to the CEO. He also excludes one card. The last remaining card is shown to all players. If the card says that it belongs to supporters, then the point goes to their piggy bank, if to opponents, then they get the point, respectively.

### End of the game
The game lasts until one of the teams fulfills the conditions necessary to win.