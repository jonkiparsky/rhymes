from rhymes import (
    max_stress,
    read_cmu_dict,
)

class TestReadDictionary:
    def test_read_good_dictionary(self):
        words, phonemes = read_cmu_dict("tests/test_data/fake_dictionary.txt")
        assert "cat" in words
        
class TestMaxStress:
    def test_max_stress(self):
        phonemes = "B IH0 G AE1 T".split(" ")
        assert max_stress(phonemes) == 3
