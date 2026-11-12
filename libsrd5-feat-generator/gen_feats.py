"""Generate Feat enum values and FeatTextResource cases for the SRD racial and class features.

Run against a checkout where libsrd5/ogl/Feats.cs and TextResources.cs are the origin/main versions.

Usage: python3 -I gen_feats.py <repo-root> <5e-database/src/2014/en> <SRD-OGL_V5.1 as text (pdftotext)>

Rules:
- Feature list from the 5e-database JSON; every description is taken from the SRD 5.1 text.
  JSON text that differs from the SRD only in case, punctuation or dashes is replaced by the
  SRD wording. Anything else must be resolved by hand (SRD_TEXT / REMOVE below), otherwise the
  script stops.
- Copies (features whose JSON text equals that of an earlier feature) are dropped.
- Double dashes and em dashes become " - ".
- Names in RENAMES get the prefix of their origin (last step).
"""
import json
import re
import sys
from collections import OrderedDict

repo, db, srd_path = sys.argv[1], sys.argv[2], sys.argv[3]
FEATS = repo + '/libsrd5/ogl/Feats.cs'
TEXTS = repo + '/libsrd5/ogl/TextResources.cs'

features = json.load(open(db + '/5e-SRD-Features.json'))
traits = {t['index']: t for t in json.load(open(db + '/5e-SRD-Traits.json'))}
races = {r['index']: r for r in json.load(open(db + '/5e-SRD-Races.json'))}
subraces = {r['index']: r for r in json.load(open(db + '/5e-SRD-Subraces.json'))}

ABILITY = {'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
           'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma'}


def norm(s):
    return re.sub(r'[^A-Z0-9]+', '_', s.upper()).strip('_')


def dashes(s):
    s = re.sub(r'\s*(--|\u2014|\u2013)\s*', ' - ', s)
    return s


# ---------------------------------------------------------------- SRD text
def clean(s):
    for a, b in (('\u2019', "'"), ('\u2018', "'"), ('\u201c', '"'), ('\u201d', '"'), ('\u00ad', ''),
                 ('\ufb01', 'fi'), ('\ufb02', 'fl'), ('\u2022', ''), ('\x0c', ' ')):
        s = s.replace(a, b)
    return s


SRD = clean(open(srd_path).read())
SRD = re.sub(r'(\w)-\n(\w)', '\\1\x00\\2', SRD)  # hyphen at a line break: decided per word later
SRD = re.sub(r'[\u2010\u2011\u2012]+-?|-[\u2010\u2011\u2012]+', '-', SRD)  # unicode hyphen variants
SRD = re.sub(r'\s+', ' ', SRD)
# page footers interrupt paragraphs
SRD = re.sub(r' ?Not for resale\. Permission granted to print or photocopy this document for personal use only\. '
             r'System Reference Document 5\.1 \d+ ?', ' ', SRD)
SRD_STRICT = dashes(SRD.replace('\x00', '-'))
SRD_STRICT_NOHY = dashes(SRD.replace('\x00', ''))
# loose form: lowercase letters and digits only, with a map back to SRD positions
loose_chars, loose_map = [], []
for i, c in enumerate(SRD):
    if c.isalnum():
        loose_chars.append(c.lower())
        loose_map.append(i)
SRD_LOOSE = ''.join(loose_chars)


def loose(s):
    return ''.join(c.lower() for c in s if c.isalnum())


def srd_paragraph(p):
    """Return the SRD wording of paragraph p, or None if the words differ."""
    p = dashes(p)
    if p in SRD_STRICT or p in SRD_STRICT_NOHY:
        return p
    lp = loose(p)
    if not lp:
        return p
    i = SRD_LOOSE.find(lp)
    if i < 0:
        return split_by_table(p)
    start, end = loose_map[i], loose_map[i + len(lp) - 1] + 1
    # extend to the end of the sentence punctuation
    while end < len(SRD) and SRD[end] in '.,;:!?)"\'':
        end += 1
    text = SRD[start:end]

    def hy(m):  # hyphen at line break: keep it if the JSON has the hyphenated word
        a, b = m.group(1), m.group(2)
        return a + '-' + b if (a + '-' + b) in p else a + b
    text = re.sub(r'(\w+)\x00(\w+)', hy, text)
    return dashes(text.strip())


def split_by_table(p):
    """The two-column PDF layout sometimes puts a table in the middle of a paragraph. Accept p if
    a leading part of it and the rest are found in the SRD close to each other."""
    words = p.split()
    for k in range(len(words) - 2, 2, -1):
        a, b = loose(' '.join(words[:k])), loose(' '.join(words[k:]))
        i = SRD_LOOSE.find(a)
        if i < 0:
            continue
        # the PDF's column order can also put the rest before the first part
        if b in SRD_LOOSE[max(0, i - 4000):i + len(a) + 4000]:
            return p
        return None
    return None


# ---------------------------------------------------------------- manual decisions
# filled after reviewing the SRD 5.1 PDF; see below
SRD_TEXT = {}
REMOVE = set()
FIXES = {}
RENAMES = {}
# renamed entries for features the JSON splits into numbered copies: index of the kept copy -> (enum, name)
MERGED = {}

exec(open(__file__.replace('gen_feats.py', 'gen_feats_manual.py')).read())


def srd_text(enum, desc_paragraphs):
    if enum in SRD_TEXT:
        return SRD_TEXT[enum]
    out = []
    for p in desc_paragraphs:
        for a, b in FIXES.get(enum, []):
            p = p.replace(a, b)
        prefix = ''
        m = re.match(r'(- )(.*)', p, re.S)  # JSON list items
        if m:
            prefix, p = m.group(1), m.group(2)
        s = srd_paragraph(p)
        if s is None:
            raise LookupError(enum)
        out.append(prefix + s)
    return '\n'.join(out)


problems = []


def entry(enum, name, desc):
    if enum in REMOVE:
        return None
    try:
        return (enum, name, srd_text(enum, desc))
    except LookupError:
        problems.append((enum, desc))
        return None


# ---------------------------------------------------------------- racial
def trait(enum, index):
    t = traits[index]
    return entry(enum, t['name'], t['desc'])


def increase(enum, race=None, subrace=None, extra=''):
    r = races[race] if race else subraces[subrace]
    parts = ['your %s score increases by %d' % (ABILITY[b['ability_score']['index']], b['bonus'])
             for b in r['ability_bonuses']]
    text = parts[0] if len(parts) == 1 else ', '.join(parts[:-1]) + ', and ' + parts[-1]
    # generated from the JSON numbers; srd_text() verifies the wording against the SRD
    return entry(enum, 'Ability Score Increase', [text[0].upper() + text[1:] + extra + '.'])


racial = OrderedDict()
racial['Elves'] = [trait('TRANCE', 'trance')]
racial['High Elves'] = [trait('HIGH_ELVEN_EXTRA_LANGUAGE', 'extra-language')]
racial['Halflings'] = [
    increase('HALFLING_ABILITY_INCREASE', race='halfling'),
    trait('HALFLING_LUCKY', 'lucky'),
    trait('HALFLING_BRAVE', 'brave'),
    trait('HALFLING_NIMBLENESS', 'halfling-nimbleness'),
    increase('LIGHTFOOT_HALFLING_ABILITY_INCREASE', subrace='lightfoot-halfling'),
    trait('NATURALLY_STEALTHY', 'naturally-stealthy'),
]
racial['Dragonborn'] = [
    increase('DRAGONBORN_ABILITY_INCREASE', race='dragonborn'),
    trait('DRACONIC_ANCESTRY', 'draconic-ancestry'),
    trait('DRAGONBORN_BREATH_WEAPON', 'breath-weapon'),
    trait('DRAGONBORN_DAMAGE_RESISTANCE', 'damage-resistance'),
]
racial['Gnomes'] = [
    increase('GNOMISH_ABILITY_INCREASE', race='gnome'),
    trait('GNOMISH_DARKVISION', 'darkvision'),
    trait('GNOMISH_CUNNING', 'gnome-cunning'),
    increase('ROCK_GNOMISH_ABILITY_INCREASE', subrace='rock-gnome'),
    trait('ARTIFICERS_LORE', 'artificers-lore'),
    trait('TINKER', 'tinker'),
]
racial['Half-Elves'] = [
    increase('HALF_ELVEN_ABILITY_INCREASE', race='half-elf',
             extra=', and two other ability scores of your choice increase by 1'),
    trait('HALF_ELVEN_DARKVISION', 'darkvision'),
    trait('SKILL_VERSATILITY', 'skill-versatility'),
]
racial['Half-Orcs'] = [
    increase('HALF_ORC_ABILITY_INCREASE', race='half-orc'),
    trait('HALF_ORC_DARKVISION', 'darkvision'),
    trait('MENACING', 'menacing'),
    trait('RELENTLESS_ENDURANCE', 'relentless-endurance'),
    trait('SAVAGE_ATTACKS', 'savage-attacks'),
]
racial['Tieflings'] = [
    increase('TIEFLING_ABILITY_INCREASE', race='tiefling'),
    trait('TIEFLING_DARKVISION', 'darkvision'),
    trait('HELLISH_RESISTANCE', 'hellish-resistance'),
    trait('INFERNAL_LEGACY', 'infernal-legacy'),
]
for k in racial:
    racial[k] = [e for e in racial[k] if e]

# ---------------------------------------------------------------- class
# enum names already present for the barbarian; their texts stay as they are
EXISTING = {'rage': 'RAGE', 'barbarian-unarmored-defense': 'UNARMORED_DEFENSE',
            'reckless-attack': 'RECKLESS_ATTACK', 'danger-sense': 'DANGER_SENSE', 'frenzy': 'FRENZY'}
# names that would collide with existing (monster) feats
RENAME = {'cunning-action': 'ROGUE_CUNNING_ACTION'}

classes = OrderedDict()
asi = next(f for f in features if f['index'] == 'barbarian-ability-score-improvement-1')
classes['All classes'] = [entry('ABILITY_SCORE_IMPROVEMENT', asi['name'], asi['desc'])]
seen = set()
for f in features:
    idx = f['index']
    key = '\n'.join(f['desc'])
    if '-ability-score-improvement-' in idx:
        # fighter (6th, 14th) and rogue (10th) get extra improvements: one value per class
        extra = {'fighter': (6, 14), 'rogue': (10,)}.get(f['class']['index'])
        if extra and f['level'] == extra[0]:
            classes.setdefault(f['class']['name'], []).append(
                entry(norm(f['class']['index']) + '_ABILITY_SCORE_IMPROVEMENT', f['name'], f['desc']))
        continue
    if key in seen:  # copy of an earlier feature
        continue
    seen.add(key)
    if idx in EXISTING:
        e = (EXISTING[idx], None, None)
    elif idx in MERGED:
        e = entry(MERGED[idx][0], MERGED[idx][1], f['desc'])
    elif idx in RENAME:
        e = entry(RENAME[idx], f['name'], f['desc'])
    elif idx.startswith('spellcasting-'):
        e = entry(norm(idx[len('spellcasting-'):]) + '_SPELLCASTING', f['name'], f['desc'])
    else:
        e = entry(norm(idx), f['name'], f['desc'])
    if e:
        classes.setdefault(f['class']['name'], []).append(e)
for k in classes:
    classes[k] = [e for e in classes[k] if e]

if problems:
    with open(srd_path + '.problems.txt', 'w') as out:
        for enum, desc in problems:
            out.write('### %s\n%s\n\n' % (enum, '\n'.join(desc)))
    print('unresolved:', len(problems), [p[0] for p in problems])
    sys.exit(1)

# ---------------------------------------------------------------- Feats.cs (CRLF)
src = open(FEATS, newline='').read()
assert '\r\n' in src
src = src.replace('\r\n', '\n')

enum_block = src[src.index('enum Feat {'):]
enum_block = enum_block[:enum_block.index('}')]
existing = set(x.strip() for x in re.sub(r'//.*', '', enum_block).split('{', 1)[1].split(',') if x.strip())

new_names = [e[0] for g in racial.values() for e in g] + \
            [e[0] for g in classes.values() for e in g if e[1] is not None]
clash = [n for n in new_names if n in existing]
assert not clash, clash
assert len(new_names) == len(set(new_names)), 'duplicate generated names'

racial_enum = ''.join('        // %s\n' % race + ''.join('        %s,\n' % e[0] for e in entries)
                      for race, entries in racial.items())
marker = '        HUMAN_ABILITY_INCREASE,\n'
assert src.count(marker) == 1
src = src.replace(marker, marker + racial_enum)

class_enum = ''.join('        // %s\n' % cls + ''.join('        %s,\n' % e[0] for e in entries)
                     for cls, entries in classes.items())
old_class = re.search(r'        // Class Feats\n.*?(?=\n\s*// Monster Feats)', src, re.S)
src = src[:old_class.start()] + '        // Class Feats\n' + class_enum + src[old_class.end():]
open(FEATS, 'w', newline='').write(src.replace('\n', '\r\n'))

# ---------------------------------------------------------------- TextResources.cs (LF)
txt = open(TEXTS, newline='').read()
assert '\r\n' not in txt


def cs(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def cases(entries, field):
    grouped = OrderedDict()
    for e in entries:
        if e[field] is not None:
            grouped.setdefault(e[field], []).append(e[0])
    return ''.join(''.join('                case Feat.%s:\n' % e for e in es) +
                   '                    return %s;\n' % cs(v) for v, es in grouped.items())


all_racial = [e for g in racial.values() for e in g]
all_class = [e for g in classes.values() for e in g]

split = txt.index('        public static string Description(this Feat feat) {')
end = txt.index('    public static class SkillTextResource')
parts = [txt[:split], txt[split:end], txt[end:]]


def inject(section, racial_cases, class_cases):
    i = section.index('                case Feat.RAGE:\n')
    section = section[:i] + racial_cases + section[i:]
    m = re.search(r'(                // Monster Feats\n)?                case Feat\.ABERRANT_GROUND:\n', section)
    return section[:m.start()] + class_cases + section[m.start():]


head = parts[0].index('    public static class FeatTextResource')
parts[0] = parts[0][:head] + inject(parts[0][head:], cases(all_racial, 1), cases(all_class, 1))
parts[1] = inject(parts[1], cases(all_racial, 2), cases(all_class, 2))
txt = ''.join(parts)

# texts for racial feats that existed before but had none (verified against the SRD)
for enum, name, desc in PREEXISTING_TEXTS:
    if name:
        a = '                case Feat.ELVEN_DARKVISION:\n                    return "Darkvision";\n'
        assert txt.count(a) == 1
        txt = txt.replace(a, a + '                case Feat.%s:\n                    return %s;\n' % (enum, cs(name)))
    b = '                case Feat.DWARVEN_RESILIENCE:\n                    return "You have advantage'
    assert txt.count(b) == 1
    txt = txt.replace(b, '                case Feat.%s:\n                    return %s;\n' % (enum, cs(desc)) + b)


def rename(text):
    for a, b in RENAMES.items():
        assert not re.search(r'\b%s\b' % b, text), 'name already in use: ' + b
        text = re.sub(r'\b%s\b' % a, b, text)
    return text


open(TEXTS, 'w', newline='').write(rename(txt))
feats = open(FEATS, newline='').read()
open(FEATS, 'w', newline='').write(rename(feats))

print('racial added:', len(all_racial))
print('class added:', sum(1 for e in all_class if e[1] is not None))
