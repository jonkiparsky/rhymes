from rhymes import (
    classify_rhymes,
    get_rhyme_groups,
    max_stress,
    rate_rhyme,
    read_cmu_dict,
)

PATH_TO_TEST_DICT = "tests/test_data/fake_dictionary.txt"
WORD_KEYS, SYL_KEYS = read_cmu_dict(PATH_TO_TEST_DICT) 

class TestReadDictionary:
    def test_read_good_dictionary(self):
        words, phonemes = read_cmu_dict(PATH_TO_TEST_DICT)
        assert "cat" in words
        
class TestMaxStress:
    def test_max_stress(self):
        phonemes = "B IH0 G AE1 T".split(" ")
        assert max_stress(phonemes) == 3


class TestRateRhyme:
    def test_rate_identical_word(self):
        word = "cat"
        assert 1.0 == rate_rhyme(word, word, WORD_KEYS)

    def test_rate_non_rhyme(self):
        word1 = "cat"
        word2 = "xylophone"
        assert 0.0 == rate_rhyme(word1, word2, WORD_KEYS)



class TestGetRhymeGroups:
    def test_get_groups_for_aa_masc_rhyme(self):
        words= ["cat", "rat"]
        groups = get_rhyme_groups(words, WORD_KEYS)
        assert groups == [{'cat', 'rat'}]

    def test_get_groups_for_ab_non_rhyme(self):
        words = ["cat", "dog"]
        groups = get_rhyme_groups(words, WORD_KEYS)
        assert groups == []

        
class TestClassifyRhymes:
    def test_classify_aa_masc_rhymes(self):
        words= ["cat", "rat"]
        groups = get_rhyme_groups(words, WORD_KEYS)
        classes = classify_rhymes(words, words, groups)
        assert classes ==['group-0', 'group-0']

    
