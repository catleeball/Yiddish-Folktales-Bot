# Yiddish Folktale Bot

A bot that automatically posts folktales from the book [*"Yiddish Folktales"*](https://mitpressbookstore.mit.edu/book/9780805210903). Tales were gathered in the 1920s and 1930s in Eastern Europe.

Posts include both the tales themselves, plus related glossary terms and annotations.

Currently posts to Cohost at https://cohost.org/Yiddish-Folktales


## Contributing

Feel free to send any drive-by bugs or PRs.

All the logic lives in main.py, each folktale is stored by their chapter number under `./data/tales/`.

Please keep the code simple and readable. Since it runs only twice a day and with no SLA, we don't care too much about efficiency.


## Operation

This script is run twice daily by [cron](https://en.wikipedia.org/wiki/Cron) on my desktop machine using the following:

`0 7,19 * * *  yiddish_folktale_bot.sh`

Login credentials must be provided in a file `secrets.py` with variable names corresponding to how they're imported in main.py.

Note that this script tracks which tale to post by storing the tale it should post on its next run in `./CURRENT_TALE.txt`. Once it posts its final tale, it starts from the beginning again with tale 1.

The script prints TSV data for logging with three columns: timestamp, post number, URL. In error messages, the post number is 0 and the URL is the error message.


## How did you make this?

I took the epub edition of this book and converted it to markdown with [Calibre](https://calibre-ebook.com). I trimmed off the introductory portion and split the glossary and annotations into separate files by hand. Then I used the regex find-replace feature in PyCharm to pre-process the text, removing some typographic oddities from the automatic markdown conversion.

Finally, I split the tales into individual markdown chapters, numbered by chapter in the book, using a quick Python script in the interpreter that I unfortunately didn't save anywhere.

I then copied the glossary and annotations markdown text into python files, and again used regex find-replace to format them into Python dictionary syntax.

Then I wrote main.py. :)


## License

All code here is your choice of [CC0 v1.0](https://creativecommons.org/publicdomain/zero/1.0/legalcode) or the [MIT license](https://mit-license.org/license.txt).

The full text of *"Yiddish Folktales"* is copyright Penguin Random House LLC and is not published in this repository in its entirety.

The folktales here fall under public domain.
