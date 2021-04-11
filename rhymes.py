from collections import defaultdict
import string
import itertools

from render import render_results

DEFAULT_RHYME_THRESHOLD = 0.7

trans_table = str.maketrans("", "", string.punctuation)

CLEAN_LINE_ERROR = "Did not find whitespace in string \"{}\". Returning input."

# Getting CMU dictionary data
# download current CMU data from
#
# note that github version modified format, so can't use that here
# this time, I'm being a little fancier and not clobbering alternates -
# this makes  handling the results a little more annoying, though


def read_cmu_dict(path_to_cmu_dict="dicts/cmudict.txt"):
    """Assumes a copy of the cmu dict is living on disk.
    For convenience, repo includes this data, which lives at
    http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/
    Note: it is also possible to get a version of the CMU
    dictionary from NLTK, but it is in a slightly different format
    and should not be loaded using this function.
    """
    cmu_phonemes = defaultdict(list)  # maps words to phonemes
    cmu_words = defaultdict(list)      # maps phonemes to words
    # both names are lousy, sorry. the intent is that we get phonemes
    # from `cmu_phonemes` and vice versa.

    f = open(path_to_cmu_dict, encoding="latin-1")
    for line in f:
        if line.startswith(";"):
            continue
        if not line.strip():
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
    if delimiter in clean_line:
        index = str.rindex(clean_line, delimiter)
        last = clean_line[index + 1:]
    else:
        last = clean_line
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


def rate_rhyme(word_1, word_2, word_keys):
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
    except ValueError:
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


def get_rhyme_groups(last_words, word_keys, threshold=DEFAULT_RHYME_THRESHOLD):
    '''
      Process:
      - get all the possible pairings of last words
      - if a pair rhymes, check and see if it rhymes with a known group
      - if it rhymes with a known group, add the pair there. if not, make a
        new rhyme group
    '''
    rhyme_groups = []
    for pair in list(itertools.combinations(last_words, 2)):
        rhyme = rate_rhyme(pair[0], pair[1], word_keys) > threshold
        if rhyme:
            matched = False
            for idx, group in enumerate(rhyme_groups):
                rhyme_rating = rate_rhyme(pair[0],
                                          next(iter(group)),
                                          word_keys)
                if rhyme_rating > threshold:
                    group.update(pair)
                    matched = True
                    break
            if not matched:
                rhyme_groups.append(set(pair))
    return rhyme_groups



def classify_rhymes(last_words, lines, rhyme_groups):
    """Given a list of "words" (should these be words, or should they
    be, perhaps, feet?) and rhyme classifications, assign the words to
    the appropriate classifications
    """
    classes = []
    for line, word in zip(lines, last_words):
        found_rhyme = False
        for idx, rhyme_group in zip(string.ascii_uppercase, rhyme_groups):
            if word in rhyme_group:
                found_rhyme = True
                classes.append(idx)
                break
        if not found_rhyme:
            classes.append("default")
    return classes


def generate_html_report(stripped_lines,
                         classes,
                         fname="output",
                         title="Title"):
    """Given a list of lines and a list of rhyme classes, produce
    a pretty report about the lines and their rhymes.
    """
    filepath = r"output/{}.html".format(fname)
    f = open(filepath, "w")
    f.write(render_results(title=title,
                           stanzas=[[(line[0:line.rindex(' ')],
                                      line[line.rindex(' '):],
                                      "group-{}".format(class_name))
                                     for line, class_name in zip(stripped_lines,
                                                                 classes)
                                     if " " in line]]))
    print("Wrote output to {}".format(filepath))


def analyze_rhyme(lines, word_keys=None):
    '''Take a sequence of lines and perform some analysis on it.
    Currently this is called for a side-effect, it produces an html
    report on disk.
    Better would be to return the analysis and allow the user to make
    use of it as they prefer.
    '''
    if word_keys is None:
        word_keys, _ = read_cmu_dict()
    tails = last_words(lines)
    rhyme_groups = get_rhyme_groups(tails, word_keys)
    rhyme_classes = classify_rhymes(tails, lines, rhyme_groups)
    return rhyme_classes


def last_words(lines):
    return [strip_punctuation(last_word(line)) for line in lines]

def load_verses(path_to_file, strip_empty_lines=False):
    '''Convenience function for getting material to work with
    '''
    lines = [line.strip() for line in open(path_to_file).readlines()]
    if strip_empty_lines:
        lines = [line for line in lines if line]
    return lines


# demonstrate usage
def how_we_do_it():
    word_keys, syl_keys = read_cmu_dict()
    poem = load_verses("texts/housman/shropshire0.txt")
    rhyme_classes = analyze_rhyme(poem, word_keys)
    generate_html_report(poem, rhyme_classes)

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
