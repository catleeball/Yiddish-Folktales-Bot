from annotations import ANNOTATIONS
from cohost.models.user import User
from cohost.models.block import MarkdownBlock
from collections import deque
from datetime import datetime
from glossary import GLOSSARY
from itertools import islice
from pathlib import Path
from secrets import COHOST_COOKIE


CURRENT_TALE_FILE = 'CURRENT_TALE.txt'
TALES_DIR = 'data/tales'
MAX_TALE_NUM = 178
TAGS = ['Yiddish Folktales', 'Jewish Folktales', 'bot account', 'automated post', 'cohost.py', 'The Cohost Bot feed']
COHOST_PAGE = 'Yiddish-Folktales'


def main():
    tale_num = get_current_tale_num()
    tale = get_tale(tale_num)
    tale_gloss_entries = get_glossary_entries(tale)
    tale_annotation = get_annotations(tale_num)
    post_body = make_post_body(tale, tale_gloss_entries, tale_annotation)
    post_to_cohost(tale_num, post_body)
    increment_tale_num(tale_num)


def get_current_tale_num() -> int:
    """Get what tale we should currently consider from a state file"""
    if not Path.exists(Path(CURRENT_TALE_FILE)):
        print(f'{datetime.now()}\t0\tERROR: Cant find current tale file: {CURRENT_TALE_FILE}')
        exit(1)

    with open(CURRENT_TALE_FILE, 'r') as f:
        current_tale = f.read()
        current_tale = current_tale.strip()

        if not current_tale.isdigit():
            print(f'{datetime.now()}\t0\tERROR: Current tale file should only contain a positive integer. Contains: {current_tale}')

        current_tale = int(current_tale)
        if current_tale < 1:
            print(f'{datetime.now()}\t0\tERROR: Current tale int must be > 0')

        # We've posted the final tale. Restart with the first one.
        if current_tale > MAX_TALE_NUM:
            current_tale = 1

        return current_tale


def get_tale_path(tale_num: int) -> str:
    return f'{TALES_DIR}/{tale_num}.md'


def get_tale(tale_num: int) -> str:
    """Get the markdown-formatted tale text for the current tale from file"""
    tale_path = get_tale_path(tale_num)

    # Make sure the file exists, or exit with an error
    if not Path.exists(Path(CURRENT_TALE_FILE)):
        print(f'{datetime.now()}\t0\tERROR: Cant find tale: {tale_path}')
        exit(1)

    with open(tale_path, 'r') as f:
        tale = f.read()
    tale = tale.strip()

    return tale


def update_post_glossary(words: list[str], gloss_entries: dict[str, str]):
    word = ' '.join(words)
    if word in GLOSSARY:
        gloss_entries[word] = GLOSSARY[word]
    elif word.lower() in GLOSSARY:
        gloss_entries[word] = GLOSSARY[word.lower()]
    return gloss_entries


def get_glossary_entries(tale: str) -> dict[str, str]:
    """Get a dictionary of relevant glossary entries for this tale"""
    words = tale.split()
    # many of the glossary words are in markdown italic; remove the asterisks for matching with the glossary dict
    words = [word.replace('*', '') for word in words]
    gloss_entries = {}

    if not words:
        print(f'{datetime.now()}\t0\tERROR: No words parsed from tale: {tale}')
        exit(1)

    # Check if each word is in the glossary
    for word in words:
        gloss_entries = update_post_glossary([word], gloss_entries)
    # Glossary entries can also be two or three word phrases.
    for word in sliding_window(words, 2):
        gloss_entries = update_post_glossary(words, gloss_entries)
    for word in sliding_window(words, 3):
        gloss_entries = update_post_glossary(words, gloss_entries)

    return gloss_entries


def get_annotations(tale_num: int) -> str:
    return ANNOTATIONS[tale_num]


def make_post_body(tale: str, gloss: dict[str, str], annot: str) -> str:
    """Compose the text of our post, combining the tale, relevant glossary entries, and annotations."""
    # format glossary
    # todo: add glossary items as markdown footnotes on the first occurrence of a glossary word in a tale
    gloss_lines: list[str] = []
    for keyword, definition in sorted(gloss.items()):
        # Cohost doesn't parse markdown inside HTML blocks, so we bold this is html tags
        line = f'<b>{keyword}</b>:  {definition}'
        gloss_lines.append(line)
    gloss_text: str = '<br>'.join(gloss_lines)

    # Since everything in the <details> tag is HTML, let's replace the newlines in the annotations with <br>
    annot.replace('\n', '<br>')

    # put the annotations & glossary in collapsible blocks
    glossary_block =   f'<details open><summary>Glossary</summary>{gloss_text}</details>'
    annotation_block = f'<details open><summary>Annotations</summary>{annot}</details>'

    body = f'{tale}\n\n\\* \\* \\*\n\n{glossary_block}\n\n\\* \\* \\*\n\n{annotation_block}\n\n'
    return body


def post_to_cohost(tale_num: int, post: str):
    user = User.loginWithCookie(COHOST_COOKIE)
    project = user.getProject(COHOST_PAGE)
    TAGS.append(f'Yiddish Folktale number {tale_num}')
    new_post = project.post(
        headline=str(tale_num),
        blocks=[MarkdownBlock(post)],
        tags=TAGS,
    )
    # Print TSV data for logging
    print(f'{datetime.now()}\t{tale_num}\t{new_post.url}')


def sliding_window(iterable, n: int):
    """From itertools recipes: https://docs.python.org/3/library/itertools.html#itertools-recipes"""
    # sliding_window('ABCDEFG', 4) --> ABCD BCDE CDEF DEFG
    it = iter(iterable)
    window = deque(islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for x in it:
        window.append(x)
        yield tuple(window)


def increment_tale_num(tale_num: int):
    with open(CURRENT_TALE_FILE, 'w') as f:
        f.write(str(tale_num + 1))


if __name__ == '__main__':
    main()
