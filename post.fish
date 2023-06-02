#!/usr/bin/env fish

# Post a Yiddish folktale to cohost.
#
# This runs as a cron job:
#     0 7,19 * * *  fish post.fish

cd /home/cat/Services/YiddishFolktaleBot
conda activate yfolk
python main.py &>> yiddish_folktale_bot.log
