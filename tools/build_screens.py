#!/usr/bin/env python3
"""Regenerate the screenshots row from whatever is in assets/screens/.

GitHub Pages serves static files with no directory index, so the page cannot
discover its own screenshots at runtime. This writes them into the HTML
instead, which also keeps the alt text in the markup for search and
screen readers.

Run after adding, removing or renaming anything in assets/screens/:

    python3 tools/build_screens.py

Order is alphabetical. To control it, prefix filenames with numbers —
01-float_idea.png, 02-event_picnic.png — and the prefix is stripped from
the alt text lookup.
"""
import pathlib, re, sys

ROOT    = pathlib.Path(__file__).resolve().parent.parent
SCREENS = ROOT / 'assets' / 'screens'
EXTS    = {'.png', '.jpg', '.jpeg'}

# Keyed by filename without any NN- prefix or extension.
ALT = {
    'float_idea':   ("Floating an idea in Catchup: picking a hike, a day and a place, ready to save",
                     "Lancer une idée dans Catchup : choisir une randonnée, un jour et un lieu, prêt à enregistrer"),
    'event_picnic': ("A Catchup picnic at Buttes-Chaumont, with who's going, the time and a map",
                     "Un pique-nique Catchup aux Buttes-Chaumont, avec les participants, l'heure et une carte"),
    'event_run':    ("A Catchup run along the canal, with who's going, the time and a map",
                     "Un footing Catchup le long du canal, avec les participants, l'heure et une carte"),
    'chat':         ("A Catchup chat where friends settle on rooftop drinks tomorrow at 19:00",
                     "Une conversation Catchup où des amis se mettent d'accord pour un verre en rooftop demain à 19:00"),
    'memories':     ("A Catchup friend profile showing what's coming up, photos from past events and mutual friends",
                     "Un profil d'ami Catchup montrant les événements à venir, des photos et des amis en commun"),
}

def key(path):
    return re.sub(r'^\d+[-_]', '', path.stem)

def figures(lang):
    out, missing = [], []
    for f in sorted(p for p in SCREENS.iterdir() if p.suffix.lower() in EXTS):
        k = key(f)
        if k in ALT:
            alt = ALT[k][0 if lang == 'en' else 1]
        else:
            alt = k.replace('_', ' ').replace('-', ' ').capitalize() + ' screen in Catchup'
            missing.append(f.name)
        src = f'assets/screens/{f.name}' if lang == 'en' else f'../assets/screens/{f.name}'
        out.append('        <figure class="phone">\n'
                   f'          <img loading="lazy" decoding="async" src="{src}" alt="{alt}" />\n'
                   '        </figure>')
    return '\n'.join(out), missing

START, END = '<!-- screens:start -->', '<!-- screens:end -->'

def main():
    files = sorted(p.name for p in SCREENS.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        print('no screenshots found', file=sys.stderr); return 1
    warned = False
    for page, lang in [('index.html', 'en'), ('fr/index.html', 'fr')]:
        p = ROOT / page
        s = p.read_text()
        if START not in s:
            print(f'{page}: missing {START} marker', file=sys.stderr); return 1
        block, missing = figures(lang)
        a = s.index(START) + len(START)
        b = s.index(END)
        p.write_text(s[:a] + '\n' + block + '\n      ' + s[b:])
        if missing and not warned:
            print('  no alt text for: ' + ', '.join(missing) + '  (add to ALT in this script)')
            warned = True
        print(f'  {page}: {len(files)} screenshots')
    print('  order: ' + ' -> '.join(files))
    return 0

if __name__ == '__main__':
    sys.exit(main())
