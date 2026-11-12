# Manual decisions for gen_feats.py, made by checking the SRD 5.1 (OGL) PDF.
# Executed inside gen_feats.py.

# Features the JSON splits into numbered copies; the first copy is kept under the plain feature name.
MERGED = {
    'barbarian-extra-attack': ('EXTRA_ATTACK', 'Extra Attack'),
    'brutal-critical-1-die': ('BRUTAL_CRITICAL', 'Brutal Critical'),
    'bardic-inspiration-d6': ('BARDIC_INSPIRATION', 'Bardic Inspiration'),
    'song-of-rest-d6': ('SONG_OF_REST', 'Song of Rest'),
    'bard-expertise-1': ('BARD_EXPERTISE', 'Expertise'),
    'magical-secrets-1': ('MAGICAL_SECRETS', 'Magical Secrets'),
    'domain-spells-1': ('DOMAIN_SPELLS', 'Domain Spells'),
    'destroy-undead-cr-1-2-or-below': ('DESTROY_UNDEAD', 'Destroy Undead'),
    'wild-shape-cr-1-4-or-below-no-flying-or-swim-speed': ('WILD_SHAPE', 'Wild Shape'),
    'circle-spells-1': ('CIRCLE_SPELLS', 'Circle Spells'),
    'fighter-fighting-style-archery': ('FIGHTING_STYLE_ARCHERY', 'Fighting Style: Archery'),
    'fighter-fighting-style-defense': ('FIGHTING_STYLE_DEFENSE', 'Fighting Style: Defense'),
    'fighter-fighting-style-dueling': ('FIGHTING_STYLE_DUELING', 'Fighting Style: Dueling'),
    'fighter-fighting-style-protection': ('FIGHTING_STYLE_PROTECTION', 'Fighting Style: Protection'),
    'fighter-fighting-style-two-weapon-fighting': ('FIGHTING_STYLE_TWO_WEAPON_FIGHTING', 'Fighting Style: Two-Weapon Fighting'),
    'action-surge-1-use': ('ACTION_SURGE', 'Action Surge'),
    'extra-attack-1': ('FIGHTER_EXTRA_ATTACK', 'Extra Attack'),
    'indomitable-1-use': ('INDOMITABLE', 'Indomitable'),
    'unarmored-movement-1': ('UNARMORED_MOVEMENT', 'Unarmored Movement'),
    'favored-enemy-1-type': ('FAVORED_ENEMY', 'Favored Enemy'),
    'natural-explorer-1-terrain-type': ('NATURAL_EXPLORER', 'Natural Explorer'),
    'rogue-expertise-1': ('ROGUE_EXPERTISE', 'Expertise'),
    'metamagic-1': ('METAMAGIC', 'Metamagic'),
    'mystic-arcanum-6th-level': ('MYSTIC_ARCANUM', 'Mystic Arcanum'),
    # the 1/rest entry already contains the paragraph about 2 and 3 uses per rest
    'channel-divinity-1-rest': ('CLERIC_CHANNEL_DIVINITY', 'Channel Divinity'),
}

# Names that are almost identical to another feat's name but mean something else get the
# prefix of their origin. Applied as the last step, so it also covers feats that existed before.
RENAMES = {
    'BONUS_PROFICIENCIES': 'BARD_BONUS_PROFICIENCIES',  # vs. the Life Domain's Bonus Proficiency
    'BONUS_PROFICIENCY': 'DIVINE_DOMAIN_BONUS_PROFICIENCY',
    'CHANNEL_DIVINITY': 'PALADIN_CHANNEL_DIVINITY',  # vs. CLERIC_CHANNEL_DIVINITY
    'UNARMORED_DEFENSE': 'BARBARIAN_UNARMORED_DEFENSE',  # vs. MONK_UNARMORED_DEFENSE
    'FIGHTING_STYLE_GREAT_WEAPON_FIGHTING': 'PALADIN_FIGHTING_STYLE_GREAT_WEAPON_FIGHTING',  # differs from the fighter's
    'SNEAK_ATTACK': 'ROGUE_SNEAK_ATTACK',  # vs. the monster feats SNEAK_ATTACK_2D6 and SNEAK_ATTACK_4D6
}

# Feats not found in the SRD 5.1
REMOVE = {
    'AURA_IMPROVEMENTS',  # the SRD has no such feature; each aura says its range increases at 18th level
    'CHANNEL_DIVINITY_2_REST',  # paragraph of the cleric's Channel Divinity (CLERIC_CHANNEL_DIVINITY)
    'DIVINE_INTERVENTION_IMPROVEMENT',  # last paragraph of Divine Intervention, which DIVINE_INTERVENTION contains
}

# Word level corrections of the JSON text; the result is still checked against the SRD
FIXES = {
    'TRANCE': [("Elves do not need", "Elves don't need"), ("After resting this way", "After resting in this way")],
    'HALFLING_BRAVE': [("saving throw against", "saving throws against")],
    'DRAGONBORN_BREATH_WEAPON': [("you cannot use it", "you can't use it")],
    'RELENTLESS_ENDURANCE': [("you cannot use this", "You can't use this")],
    'MARTIAL_ARTS': [("Table: The Monk", "the Monk table"), ("two- handed", "two-handed")],
    'KI': [("Table: The Monk", "the Monk table")],
    'UNARMORED_MOVEMENT': [("Table: The Monk", "the Monk table")],
    'DIVINE_SENSE': [("but not its identity.", "but not its identity (the vampire Count Strahd von Zarovich, for instance).")],
    'LAY_ON_HANDS': [("paladin level x 5", "paladin level \u00d7 5")],
}

# SRD 5.1 wording where the JSON text differs in its words
_DARK = (" you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it "
         "were bright light, and in darkness as if it were dim light. You can't discern color in darkness, only shades of gray.")
SRD_TEXT = {
    # the JSON has one generic darkvision text, the SRD words it per race
    'GNOMISH_DARKVISION': "Accustomed to life underground," + _DARK,
    'HALF_ELVEN_DARKVISION': "Thanks to your elf blood," + _DARK,
    'HALF_ORC_DARKVISION': "Thanks to your orc blood," + _DARK,
    'TIEFLING_DARKVISION': "Thanks to your infernal heritage," + _DARK,
    # the JSON replaces SRD sentences with notes about other publications
    'DIVINE_DOMAIN': "Choose one domain related to your deity, such as Life. Each domain is detailed at the end of the class description, and each one provides examples of gods associated with it. Your choice grants you domain spells and other features when you choose it at 1st level. It also grants you additional ways to use Channel Divinity when you gain that feature at 2nd level, and additional benefits at 6th, 8th, and 17th levels.",
    'ROGUISH_ARCHETYPE': "At 3rd level, you choose an archetype that you emulate in the exercise of your rogue abilities, such as Thief. Your archetype choice grants you features at 3rd level and then again at 9th, 13th, and 17th level.",
    'OTHERWORLDLY_PATRON': "At 1st level, you have struck a bargain with an otherworldly being of your choice: the Archfey, the Fiend, or the Great Old One, each of which is detailed at the end of the class description. Your choice grants you features at 1st level and again at 6th, 10th, and 14th level.",
}

# Pre-existing racial feats that had no text: (enum, name or None, description)
PREEXISTING_TEXTS = [
    ('HUMAN_ABILITY_INCREASE', 'Ability Score Increase', 'Your ability scores each increase by 1.'),
    ('ELVEN_DARKVISION', None, "Accustomed to twilit forests and the night sky, you have superior vision in dark and dim conditions. You can see in dim light within 60 feet of you as if it were bright light, and in darkness as if it were dim light. You can't discern color in darkness, only shades of gray."),
]
for _enum, _name, _desc in PREEXISTING_TEXTS:
    assert srd_paragraph(_desc) == _desc, _enum
for _enum, _text in SRD_TEXT.items():
    for _p in _text.split('\n'):
        assert srd_paragraph(_p.lstrip('- ')) is not None, _enum
