from rhymes import read_cmu_dict

class TestReadDictionary:
    def test_read_good_dictionary(self):
        words, phonemes = read_cmu_dict("tests/test_data/fake_dictionary.txt")
        assert "cat" in words
        
