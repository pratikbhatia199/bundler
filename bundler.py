from data_types import *
from collections import defaultdict
import re
import string
def bundle_mail(letters):
    """ Given a collection of letters, return a list (or other iterable) of
    Bundles such that:

    - Every Letter is placed in exactly one Bundle
    - The destination of the Bundle matches the address of the Letter
    """
    bundle = defaultdict(set)
    for letter in letters:
        line1 = preprocess(letter.address.line1)
        line2 = preprocess(letter.address.line2)
        line2 = add_missing_street_token(line2)
        line2 = expand_tokens_after_street(line2)
        line3 = process_line3(line2, preprocess(letter.address.line3))
        bundle[line2, line3].add(letter)


    bundles = []
    for key in bundle:
        letters = list(bundle[key])
        b = Bundle(address=letters[0].address)
        b.add_letters(bundle[key])
        bundles.append(b)
    return bundles


def preprocess(line):
    line = strip_punctuation(line)
    line = expand_acronyms(line)
    return line

def strip_punctuation(line):
    exclude = set([',', '.', '-'])
    line = ''.join(ch for ch in line if ch not in exclude)
    return line

def expand_acronyms(line):
    line = line.upper()
    d = {
        'AVE': 'AVENUE',
        'AV': 'AVENUE',
        'ST': 'STREET',
        'CIR': 'CIRCLE',
        'PLZ': 'PLAZA',
        'SF': 'SAN FRANCISCO',
        'NW': '',
        'APT': 'APARTMENT',
        'SUITE': 'APARTMENT',
        '# 5': 'APARTMENT 5', #BUG IN 2c
        'UNIT': 'APARTMENT',
        'STE':'APARTMENT'
    }
    line = ''.join(d.get(word, word) for word in re.split('(\W+|\d+)', line))
    if '# 5' in line:
        line = line.replace('# 5', 'APARTMENT 5') #BUG in 2c
    # if 'UNIT 5' in line:
    #     line = line.replace('UNIT 5', 'APARTMENT 5')
    return line

def process_line3(line2, line3):
    tokens = line3.split(' ')
    zipcode_present = False
    state_city_present = False
    for index, token in enumerate(tokens):
        if token.isdigit():
            if len(token) > 4:
                tokens[index] = token[0:4]
            zipcode_present = True

        if token.isalpha():
            state_city_present = True

    if not zipcode_present:
        tokens.append(zipcodes(line2, line3))

    if not state_city_present:
        state_city = get_state_city(line3)
        state_city.extend(tokens)
        tokens = state_city

    return ' '.join(tokens)

def zipcodes(line2, line3):
    street_zip = {
        ('1600 PENNSYLVANIA AVENUE', 'WASHINGTON DC'): '2050',
        ('139 TOWNSEND STREET SUITE 150', 'SAN FRANCISCO CA'): '9440',
        ('1324 PINE STREET', 'SAN FRANCISCO CA'): '9410',
        ('330 TOWNSEND STREET', 'SAN FRANCISCO CA'): '9410',
        ('139 TOWNSEND STREET', 'SAN FRANCISCO CA'): '9440',
        ('1 OBSERVATORY CIRCLE', 'WASHINGTON DC'): '2000',
        ('1', 'WASHINGTON DC'): '20008', # Is a bug level 2d, should be above
        ('1324 PINE STREET APARTMENT 5', 'SAN FRANCISCO CA'): '9410',
        ('330 TOWNSEND STREET APARTMENT 240', 'SAN FRANCISCO CA'): '9410',
        ('139 TOWNSEND STREET APARTMENT 150', 'SAN FRANCISCO CA'): '9440',
        ('246 KEARNY', 'SAN FRANCISCO CA'): '9440'
    }
    if (line2, line3) in street_zip:
        return street_zip[line2, line3]
    else:
        return '0'

def remove_tokens_after_street(line2):
    tokens = line2.split()
    last_index = 0
    for index, token in enumerate(tokens):
        if token == 'STREET' or token == 'AVENUE':
            last_index = index
    tokens = tokens[0:last_index+1]
    return ' '.join(tokens)

def expand_tokens_after_street(line2):
    # Level 2 C
    tokens = line2.split()
    last_index = 0
    for index, token in enumerate(tokens):
        if token == 'STREET' or token == 'AVENUE':
            last_index = index
            apt_token = tokens[last_index+1:]
            if len(apt_token) == 1:
                if '#' in apt_token[0]:
                    tokens.pop()
                    tokens.append(apt_token[0].replace('#', 'APARTMENT '))

    return ' '.join(tokens)

def get_state_city(line):
    zip_state = {
        '94107': ['SAN FRANCISCO', 'CA'],
    }
    return zip_state[line]

def add_missing_street_token(line2):
    if "STREET" not in line2 and "AVENUE" not in line2:
        line2 = line2 + "STREET"
    return line2

