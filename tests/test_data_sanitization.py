
from poem import Poem
from rhymes import load_verses

TEST_DATA_DIR = "tests/test_data"

class TestRemoveHeader:
    def test_single_line_header(self):
        poem = Poem(load_verses(f"{TEST_DATA_DIR}/single_line_title.txt"))
        assert len(poem) == 3

    def test_multiline_header(self):
        poem = Poem(load_verses(f"{TEST_DATA_DIR}/multi_line_header.txt"))
        assert len(poem) == 3

    def test_single_line_stanza(self):
        poem = Poem(load_verses(f"{TEST_DATA_DIR}/single_line_stanza.txt"))
        assert len(poem) == 5

    def test_all_single_lines(self):
        poem = Poem(load_verses(f"{TEST_DATA_DIR}/all_single_lines.txt"))
        assert len(poem) == 5

    def test_no_header(self):
        poem = Poem(load_verses(f"{TEST_DATA_DIR}/multi_line_stanzas.txt"))
        assert len(poem) == 5