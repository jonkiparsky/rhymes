from collections import defaultdict
import nltk
import string

import itertools

from render import render_results
# Sketches of code and notes about detecting rhymes in text


trans_table = str.maketrans("", "", string.punctuation)

CLEAN_LINE_ERROR = "Did not find whitespace in string \"{}\". Returning input."
# target poem
shropshire1 = ['From Clee to heaven the beacon burns,',
               'The shires have seen it plain,',
               'From north and south the sign returns',
               'And beacons burn again.',
               '',
               'Look left, look right, the hills are bright,',
               'The dales are light between,',
               "Because 'tis fifty years to-night",
               'That God has saved the Queen.',
               '',
               'Now, when the flame they watch not towers',
               'About the soil they trod,',
               "Lads, we'll remember friends of ours",
               'Who shared the work with God.',
               '',
               'To skies that knit their heartstrings right,',
               'To fields that bred them brave,',
               'The saviours come not home to-night:',
               'Themselves they could not save.',
               '',
               'It dawns in Asia, tombstones show',
               'And Shropshire names are read;',
               'And the Nile spills his overflow',
               "Beside the Severn's dead.",
               '',
               'We pledge in peace by farm and town',
               'The Queen they served in war,',
               'And fire the beacons up and down',
               'The land they perished for.',
               '',
               '"God Save the Queen" we living sing,',
               "From height to height 'tis heard;",
               'And with the rest your voices ring,',
               'Lads of the Fifty-third.',
               '',
               'Oh, God will save her, fear you not:',
               "Be you the men you've been,",
               'Get you the sons your fathers got,',
               'And God will Save the Queen.']

# Getting CMU dictionary data from NLTK
# This is just to get us something to play with, it's horrible...


def cmu_data_from_nltk():
    entries = nltk.corpus.cmudict.entries()  # nltk may require some steps
    # for this to work...
    to_phonemes = dict(entries)  # oops! Just overwrote any alternate entries!
    to_word = {(tuple(val), key) for key, val in entries}
    # to_phonemes: keys are words in lowercase, values are lists of phonemes
    # to_word inverts that dict
    return to_phonemes, to_word


# Getting CMU dictionary data w/o NLTK
# download current CMU data from
# http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/
# note that github version modified format, so can't use that here
# this time, I'm being a little fancier and not clobbering alternates -
# this makes  handling the results a little more annoying, though


def read_cmu_dict(path_to_cmu_dict):
    cmu_phonemes = defaultdict(list)  # maps words to phonemes
    cmu_words = defaultdict(list)      # maps phonemes to words
    # both names are lousy, sorry. the intent is that we get phonemes
    # from `cmu_phonemes` and vice versa.

    f = open(path_to_cmu_dict, encoding="latin-1")
    for line in f:
        if line.startswith(";"):
            continue
        word, phonemes = line.strip().split("  ")
        word = word.lower()  # normalize to lowercase
        phonemes = tuple(phonemes.split(" "))
        cmu_phonemes[word].append(phonemes)
        cmu_words[phonemes].append(word)
    return cmu_phonemes, cmu_words

# It may turn out that we prefer to write this stuff to a sqlite db and read it
# from disk rather than keep it in memory. This would have some advantages,
# including hitting one of the items on the CMU dict maintainers' wish list.


def flatten(list_of_lists):
    return [val for sublist in list_of_lists for val in sublist]


def to_phonemes(word, dictionary):
    return dictionary.get(word.lower()) or [word]


def phonemify(line, syllabary):
    words = strip_punctuation(line).split(" ")
    return [to_phonemes(word, syllabary) for word in words]


def strip_punctuation(s):
    return s.translate(trans_table)


def get_stress(phoneme):
    '''
    From a phoneme representation, return the stress marker
    (an integer in [0, 1, 2])
    :return: stress marker or None if no marker exists

    '''
    if len(phoneme) == 0:
        return
    end = phoneme[-1]
    return int(end) if end.isnumeric() else None


def humanize_stress(stress):
    '''
    Takes a CMU-defined stress (1 is primary stress, 2 is secondary stress,
    0 is no stress) and returns an integer such that primary stress >
    secondary stress > no stress.
    :param stress: CMU-defined stress marker (1 > 2 > 0)
    :return converted_stress: ordered stress marker
    '''
    conversion = {1: 2,
                  2: 1,
                  None: 0}

    return conversion.get(stress, stress)  # if not found, return what we got


def max_stress(phonemes):
    '''
    Takes a list of phonemes and returns the index of the maximum stress.
    If a tie exists, returns the first (leftmost) instance of the stress.
    :param phonemes: list of CMU-defined phonemes
    :return: index of maximum stress or None if no max exists
    '''
    assert len(phonemes) > 0
    stresses = [humanize_stress(get_stress(phoneme)) for phoneme in phonemes]
    max_stress = None
    try:
        max_stress = stresses.index(max(stresses))
    except ValueError:
        print("No maximum stress was found for phonemes {}".format(phonemes))
    return max_stress


'''
  # This implementation of split_on_stress ignores syllable onsets!
  For now operating on the assumption that when we compare the word segments,
  it doesn't matter whether those phonemes occur at the end of the first part
  or the beginning of the second. We'll see if that stands!
'''


def split_on_stress(phonemes):
    '''
    Takes a list of phonemes and returns the list as two elements: the first is
    the portion of the word up to but not including the max stressed vowel, and
    the second the portion after, including the vowel.
    :param phonemes:
    :return: A list of lists representing the split list of phonemes
    '''
    stress = max_stress(phonemes)
    return [phonemes[0:stress], phonemes[stress:]]


def split_on_final_vowel(phonemes):
    '''
    Given a list of phonemes splits the list in two where the first list
    contains the phonemes up to (but not including) the final vowel, and the
    second list is the final vowel and everything rightwards.
    If no stressed phoneme is present, returns the input.
    :param phonemes:
    :return:
    '''
    stresses = [get_stress(phoneme) for phoneme in phonemes]
    try:
        i_stress = next(i for i in reversed(range(len(phonemes)))
                        if stresses[i] is not None)
        return [phonemes[0:i_stress], phonemes[i_stress:]]
    except StopIteration:
        return phonemes


def last_word(line, delimiter=" "):
    '''
    Given a string, returns the part to the right of the last instance of the
    given delimiter.
    If no delimiter is found, returns the input
    :param line: string
    :return: substring of the input
    '''
    # there could be sneaky whitespace at the end!
    clean_line = line.strip()
    if delimiter in line:
        index = str.rindex(clean_line, delimiter)
        last = line[index + 1:]        
    else: 
        last = line
    return last


def eval_periphery(l1,
                   l2,
                   current_pts=0,
                   possible_pts=0,
                   unit_pts=1,
                   nucleus_pts=0):
    '''
    Takes two arrays of phonemes and compares them in parallel. Returns updated
    current_points and possible_points

    :param l1: list of phonemes
    :param l2: list of phonemes
    :param current_pts: aggregator for comparing parts of words independently
    :param possible_pts: aggregator for comparing parts of words independently
    :param unit_pts: number of points to assign a matching pair of phonemes
    :param nucleus_pts: points to assign the first matching phoneme pair

    (assumed to be rhyme nucleus here)
    :return:  tuple of new current_points, possible_points
    '''
    counter = 0
    for i1, i2 in zip(l1, l2):
        points = nucleus_pts if counter == 0 else unit_pts
        if i1 == i2:
            current_pts += points
        possible_pts += points
        counter += 1
    possible_pts += abs(len(l1) - len(l2))

    return current_pts, possible_pts


def rate_rhyme(word_1, word_2):
    """
    Takes two words (in English...might want to adapt this to also accept
    phoneme lists) and returns an estimate of how closely they rhyme. Values
    are between [0, 1], where higher values mean a closer match.

    This evaluation is really rough right now. I think the next place I want
    to go with it is to take phoneme classes into account so that "bat" and
    "cat" returns a higher value than "bat" and "bath"

    The current rubric is pretty naive, but it gets us a long way. Here it is:
    # rubric:
    # 10 points for matching vowel nucleus
    # rate coda as follows:
    # - for each position past the nucleus, give +5 points for each perfectly
        matching phone
    # rate "onset" as follows:
    # - for each position prior to the nucleus, give +1 point for each
        perfectly matching phone
    # syllables too?

    To be honest, you'd get pretty much the same result if you only looked at
    the rhyme nucleus, so the bit
    with "eval_periphery" is where improvements should be made.

    :param word_1: word 1 to compare
    :param word_2: word 2 to compare
    :return:
    """
    # ew gross
    phones_1 = flatten(flatten(phonemify(word_1, word_keys)))
    phones_2 = flatten(flatten(phonemify(word_2, word_keys)))
    try:
        onset_1, coda_1 = split_on_final_vowel(phones_1)
        onset_2, coda_2 = split_on_final_vowel(phones_2)
    except ValueError as e:
        # something wasn't parsed correctly
        return 0

    NUCLEUS = 10
    CODA = 3
    ONSET = 1

    possible_points = 0
    current_points = 0
    current_points, possible_points = eval_periphery(coda_1, coda_2,
                                                     current_points,
                                                     possible_points,
                                                     nucleus_pts=NUCLEUS,
                                                     unit_pts=CODA)
    current_points, possible_points = eval_periphery(onset_1,
                                                     onset_2,
                                                     current_points,
                                                     possible_points,
                                                     unit_pts=ONSET)
    return current_points / possible_points


# ok, let's see how we do
word_keys, syl_keys = read_cmu_dict("dicts/cmudict.txt")
stripped = list(filter(lambda pot_line: len(pot_line) > 0, shropshire1))
# empty lines are a crutch!
last_words = [strip_punctuation(last_word(line)) for line in stripped]

DEFAULT_RHYME_THRESHOLD = 0.7



def get_rhyme_groups(last_words, threshold=DEFAULT_RHYME_THRESHOLD):
    '''
      Process:
      - get all the possible pairings of last words
      - if a pair rhymes, check and see if it rhymes with an already-known group
      - if it rhymes with a known group, add the pair there. if not, make a
        new rhyme group
    '''

    rhyme_groups = []
    for pair in list(itertools.combinations(last_words, 2)):
        rhyme = rate_rhyme(pair[0], pair[1]) > threshold
        if rhyme:
            matched = False
            for idx, group in enumerate(rhyme_groups):
                if rate_rhyme(pair[0], next(iter(group))) > threshold:
                    group.update(pair)  # maybe only save a representative sample?
                    matched = True
                    break
            if not matched:
                rhyme_groups.append(set(pair))
    return rhyme_groups


def classify_rhymes(last_words, rhyme_groups):
    classes = []

    for line, word in zip(stripped, last_words):
        line_data = [line, word]
        found_rhyme = False
        for idx, rhyme_group in enumerate(rhyme_groups):
            if word in rhyme_group:
                found_rhyme = True
                classes.append("group-{}".format(idx))
                break
        if not found_rhyme:
            classes.append("default")
    return classes


def print_report(stripped_lines, classes):
    f = open(r"output/output.html", "w")
    f.write(render_results(lines=[(line[0:line.rindex(' ')],
                                   line[line.rindex(' '):],
                                   class_name)
                                  for line, class_name in zip(stripped, classes)]))
    

'''
# just some notes below here
# matching primary stress vowel
# number of syllables prior to stress?

# Word pair          Test

# syllable onset
# 'plod : 'prod, 'clod, 'nod, 'odd

# number of syllables prior to matching section
# 'ate : 'mate, 'e'late, 'confiscate, de'activate

# position of stress prior to matching section:
# 'trod : a'broad, 'nimrod, 'arthropod (word initial stress)
# 'trod : 'arthropod, I'ditarod, (missing one here)

# syllable coda
# 'bean: 'beat, 'bead, 'beast, 'beer,

'''
