#!/usr/bin/env python3
import sys
import datetime
import time
import yaml
import logging
logging.basicConfig(level=logging.DEBUG)
from functools import cmp_to_key
from random import Random
import feedparser

DATA = sys.argv[1]
OUT = sys.argv[1]
NOW = datetime.datetime.now()
with open(DATA, 'r', encoding='utf-8') as handle:
    conf = yaml.load(handle)


def forbiddenMeta(meta):
    for w in ('satire', 'quiz'):
        if w in meta:
            return True
    return False

def get_default(name, feedurl):
    feed = feedparser.parse(feedurl)
    logging.info("fetch "+feedurl)
    home_url = getattr(feed.feed, 'link', feedurl)
    name = '<a href="%s" class="meta">%s</a>' % (home_url, name)
    afternoon = (NOW.hour >= 12)
    for e in feed.entries:
        if not hasattr(e, 'published_parsed'):
            continue
        if not e.published_parsed:
            continue
        dt = datetime.datetime.fromtimestamp(time.mktime(e.published_parsed))
        dt_diff = NOW - dt
        if dt_diff.days > 0:
            continue # skip news older than 24h
        if afternoon and dt.day != NOW.day:
            continue # skip yesterday's news
        tags = ""
        if hasattr(e, 'tags'):
            tags += ' ' + ', '.join(i['term'] for i in e.tags)
        if forbiddenMeta(tags.lower()):
            continue
        title = getattr(e, 'title', '–')
        link = getattr(e, 'link', '')
        value = valueItem((e.link, title, name, dt, tags))
        yield e.link, title, name, dt, tags, value

def boost_it(section):
    for score_group in conf['weights'][section]:
        words = conf['weights'][section][score_group].strip().split()
        # Replace spaces
        words = [x.replace('\s', ' ') for x in words]
        yield (score_group, words)

def valueItem(item):
    value = 0
    # Value title content
    title = item[1].lower()
    for (score_group, words) in boost_it('keyword'):
        for w in words:
            if w in title:
                value += score_group

    if len(title) < 15:
        value -= 23
    if len(title) < 30:
        value -= 10
    if len(title) < 40:
        value -= 4

    # Value sources
    source = item[2].lower()
    for source_key in conf['feeds']:
        if source_key in source:
            value += conf['feeds'][source_key].get('weight', 0)

    # Source boosts
    url = item[0].lower()
    for (score_group, words) in boost_it('sources'):
        for w in words:
            if w in url:
                value += score_group

    # Value tags
    tags = item[4].lower()
    for (score_group, words) in boost_it('tags'):
        for w in words:
            if w in tags:
                value += score_group
    return value

def get_All():
    all = list()
    for source_key in conf['feeds']:
        all.extend(get_default(source_key, conf['feeds'][source_key]['url']))

    rng = Random(42)
    rng.shuffle(all)
    def mycmp(a, b):
        va = a[5]
        vb = b[5]
        if va > vb: return -1
        if va < vb: return  1
        da = a[2]
        db = b[2]
        if da > db: return -1
        if da < db: return  1
        return 0
    all.sort(key=cmp_to_key(mycmp))
    return all

def generate(fh):
    fh.write("""
<!DOCTYPE html>
<html><head><title>TextNews {NOW}</title>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<meta http-equiv="refresh" content="2000">
<style>
html, body {{ font-family: sans-serif; font-size: 99%; }}
a.meta {{ color: inherit; }}
h1 {{ font-weight:normal; }}
p.fresh time {{ background-color: #d74; color: #ffc; padding: 0 2px; }}
p.yesterday a:link {{ color: #333; }}
.value {{ color: #ccc; }}
</style>
</head><body>
<h1 style="font-size:80%">Text<b>News</b> {NOW}</h1>
    """.format(NOW=NOW.isoformat()))

    for link, title, src, dt, tags, value in get_All():
        css_classes = list()
        if ((NOW - dt).seconds) < (2 * 60 * 60) and NOW > dt:
            css_classes.append('fresh')
        if (NOW.day != dt.day):
            css_classes.append('yesterday')
        dt = dt.isoformat()
        dt = '<time datetime="%s">%s</time>' % (dt, dt.replace("T", " ")[11:-3])
        if css_classes:
            fh.write('<p class="%s">' % (' '.join(css_classes)))
        else:
            fh.write('<p>')
        if link:
            fh.write('<a href="%s">%s</a>' % (link, title))
        else:
            fh.write('<a>%s</a>' % (title,))
        fh.write(' %s %s %s <span class="value">%s</span></p>' % (src, dt, tags, value))

    fh.write('<p>Deutsche Nachrichten als reiner Text. <a href="https://github.com/qznc/textnews">Code auf GitHub</a>.</p>')
    fh.write("</body></html>")

with open(OUT, 'w', encoding='utf-8') as handle:
    generate(handle)
