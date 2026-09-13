#!/usr/bin/env python3
"""Build script for the Grump the Baby Destroyer wiki.

Static site, no framework. This script:
  1. Wraps each content/<page>.html fragment in the shared page template
     (sidebar nav, breadcrumb, footer with commit sha + date).
  2. Writes the finished pages to the wiki root.
  3. Builds search-index.json by extracting every heading (h2/h3/h4 with an
     id) plus a text snippet, for the client-side search box in js/site.js.

Run it after editing anything in content/ or after the game changes:
    python build.py [--sha <short-sha>]

If --sha is omitted it shells out to the game repo to read the current
commit, so re-running this after a game update keeps the footer honest.
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, 'content')
GAME_DIR = r"D:\code stuff\dma ai\baby-destroyer"

# (id, filename, nav label, section heading) -- order is the sidebar order.
PAGES = [
    ('home', 'index.html', 'Home', None),
    ('controls', 'controls.html', 'Controls', 'Playing'),
    ('day', 'day.html', 'The Day', 'Playing'),
    ('night', 'night.html', 'The Night', 'Playing'),
    ('difficulty', 'difficulty.html', 'Nights & Difficulty', 'Playing'),
    ('generator', 'generator.html', 'The Generator & Power', 'Playing'),
    ('items', 'items.html', 'Items', 'Reference'),
    ('loot', 'loot.html', 'Loot Tables', 'Reference'),
    ('characters', 'characters.html', 'Characters', 'Reference'),
    ('questions', 'questions.html', "Grump's Questions", 'Reference'),
    ('rooms', 'rooms.html', 'Rooms & The School', 'Reference'),
    ('lore', 'lore.html', 'Lore', 'Reference'),
    ('coop', 'coop.html', 'Co-op', 'Playing'),
    ('map', 'map.html', 'The Map', 'Reference'),
    ('tips', 'tips.html', 'Tips & Strategy', 'Guides'),
    ('faq', 'faq.html', 'FAQ / Troubleshooting', 'Guides'),
    ('changelog', 'changelog.html', 'Changelog', 'Guides'),
]
BY_ID = {p[0]: p for p in PAGES}

GAME_URL = 'https://randomprojects1234.github.io/grump-the-baby-destroyer/'
REPO_URL = 'https://github.com/RandomProjects1234/grump-the-baby-destroyer'


def get_sha():
    for a in sys.argv[1:]:
        if a.startswith('--sha='):
            return a.split('=', 1)[1]
    try:
        out = subprocess.check_output(
            ['git', '-C', GAME_DIR, 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return 'unknown'


def sidebar(active_id):
    sections = {}
    for pid, fname, label, section in PAGES:
        sections.setdefault(section, []).append((pid, fname, label))
    out = []
    out.append('<a class="playbtn" href="%s" target="_blank" rel="noopener">&#9654; Play the game</a>' % GAME_URL)
    out.append('<div class="searchbox">')
    out.append('<input id="search-input" type="text" placeholder="Search the wiki..." autocomplete="off">')
    out.append('<div id="search-results" class="searchresults"></div>')
    out.append('</div>')
    # Home link first, unsectioned
    home = sections.pop(None)
    out.append('<ul class="navlist">')
    for pid, fname, label in home:
        cls = ' class="active"' if pid == active_id else ''
        out.append('<li><a href="%s"%s>%s</a></li>' % (fname, cls, label))
    out.append('</ul>')
    n = 1
    for section in ['Playing', 'Reference', 'Guides']:
        if section not in sections:
            continue
        out.append('<h5 style="margin-top:16px">%s</h5>' % section)
        out.append('<ul class="navlist">')
        for pid, fname, label in sections[section]:
            cls = ' class="active"' if pid == active_id else ''
            out.append('<li><a href="%s"%s><span class="num">%02d</span>%s</a></li>' % (fname, cls, n, label))
            n += 1
        out.append('</ul>')
    return '\n'.join(out)


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · Grump the Baby Destroyer Wiki</title>
<meta name="description" content="{description}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'><rect width='16' height='16' fill='%230d1210'/><rect x='3' y='5' width='3' height='3' fill='%23e5a83a'/><rect x='10' y='5' width='3' height='3' fill='%23e5a83a'/><rect x='4' y='11' width='8' height='2' fill='%236f8f5a'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css">
</head>
<body data-base="">
<div class="navtoggle">&#9776;&nbsp; Grump Wiki</div>
<div class="sidebar-scrim"></div>
<div class="wrap">
  <nav class="sidebar">
    <a class="brand" href="index.html">GRUMP<span class="sub">the baby destroyer &middot; wiki</span></a>
    {sidebar}
    <div class="sidebar-foot">
      Fan wiki, not an official site.<br>
      Matches game commit <code>{sha}</code><br>
      Updated {date}
    </div>
  </nav>
  <main>
    <div class="breadcrumb"><a href="index.html">Wiki</a> / {label}</div>
    {content}
    <div class="pagefoot">
      <span>Grump the Baby Destroyer Wiki &middot; last updated {date} &middot; matches game commit <code>{sha}</code></span>
      <span><a href="{game_url}" target="_blank" rel="noopener">Play the game</a> &middot; <a href="{repo_url}" target="_blank" rel="noopener">Game source</a></span>
    </div>
  </main>
</div>
<script src="js/site.js"></script>
</body>
</html>
"""

DESCRIPTIONS = {
    'home': "The complete wiki for Grump the Baby Destroyer: a browser survival-horror game about a baby left behind in an empty school.",
    'controls': "Full control scheme for Grump the Baby Destroyer.",
    'day': "How the day phase works: Mrs. Honeywell's list, jobs, food and hunger.",
    'night': "How the night phase works: light, hiding, noise and fear.",
    'difficulty': "Nights, difficulty settings, night modifiers and escaping.",
    'generator': "The generator fuel burn formula, wear, stalling, starting and portable lights.",
    'items': "Every item in Grump the Baby Destroyer, with exact numbers.",
    'loot': "Loot tables for every container kind, with search times and odds.",
    'characters': "Bob the Janitor, Grump, the Card Kid, the Taker, and the toddlers.",
    'questions': "Every question Grump asks, every answer, and its cost. Spoilers.",
    'rooms': "Every room in the school, its furniture, hiding spots and locked doors.",
    'lore': "All twelve crayon drawings, in order. Spoilers.",
    'coop': "Hosting and joining co-op, host authority, spectating, revives and escaping together.",
    'map': "The in-game map legend.",
    'tips': "Strategy derived from the actual game mechanics.",
    'faq': "Common problems and questions, answered.",
    'changelog': "What changed in the game, commit by commit.",
}


def build_page(pid, fname, label, sha, today):
    frag_path = os.path.join(CONTENT, fname)
    with open(frag_path, encoding='utf-8') as f:
        content = f.read()
    html_out = TEMPLATE.format(
        title=label if pid != 'home' else 'Home',
        description=DESCRIPTIONS.get(pid, ''),
        sidebar=sidebar(pid),
        content=content,
        sha=sha,
        date=today,
        label=label,
        game_url=GAME_URL,
        repo_url=REPO_URL,
    )
    out_path = os.path.join(ROOT, fname)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
    return content, out_path


HEADING_RE = re.compile(r'<h([234])\s+id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
TAG_RE = re.compile(r'<[^>]+>')
TEXT_AFTER_RE = re.compile(r'</h[234]>(.*?)(?=<h[234]|\Z)', re.S)


def strip_tags(s):
    return html.unescape(TAG_RE.sub(' ', s)).strip()


def build_search_index():
    index = []
    for pid, fname, label, section in PAGES:
        frag_path = os.path.join(CONTENT, fname)
        with open(frag_path, encoding='utf-8') as f:
            content = f.read()
        # Page-level entry
        index.append({'page': label, 'url': fname, 'heading': label, 'snippet': strip_tags(content)[:180]})
        for m in HEADING_RE.finditer(content):
            hid = m.group(2)
            heading_text = strip_tags(m.group(3))
            tail_start = m.end()
            tail_match = re.search(r'(.*?)(?=<h[234]|\Z)', content[tail_start:], re.S)
            snippet = strip_tags(tail_match.group(1))[:220] if tail_match else ''
            index.append({
                'page': label,
                'url': '%s#%s' % (fname, hid),
                'heading': heading_text,
                'snippet': snippet,
            })
    with open(os.path.join(ROOT, 'search-index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False)
    return len(index)


def main():
    sha = get_sha()
    today = date.today().isoformat()
    for pid, fname, label, section in PAGES:
        build_page(pid, fname, label, sha, today)
    n = build_search_index()
    print('Built %d pages. Search index: %d entries. Game commit: %s' % (len(PAGES), n, sha))


if __name__ == '__main__':
    main()
