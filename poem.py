from itertools import chain

from rhymes import (
    read_cmu_dict,
    analyze_rhyme
    )

WORD_KEYS, _  = read_cmu_dict()

class Poem:
    def __init__(self, lines, title=""):
        self.read_lines(lines)
        self.title = title or str(self.stanzas[0].lines[0])
                                  
    def read_lines(self, lines):
        strip_lines(lines)
        self.stanzas = []
        current_stanza = []
        
        for line in lines:
            line = line.strip()
            if line:
                current_stanza.append(Line(line))
            else:
                self.stanzas.append(Stanza(current_stanza))
                current_stanza = []
        if current_stanza:
            self.stanzas.append(Stanza(current_stanza))

    def rhyme_scheme(self):
        stanza_analyses = [stanza.analyze() for stanza in self.stanzas]
        schemes = set(["".join(analysis) for analysis in stanza_analyses])
        return schemes

    def __str__(self):
        return "\n\n".join([str(stanza) for stanza in self.stanzas])

    def __repr__(self):
        identifier = self.title
        return "<Poem: {}>".format(self.title)

    def __iter__(self):
        return (line for line in chain(*self.stanzas))
        
    
class Stanza:
    '''A section of a poem/song/metrical whatnot.
    Assume for the nonce that empty lines separate stanzas. 
    '''
    
    def analyze(self):
        return analyze_rhyme([str(line) for line in self.lines], WORD_KEYS)
        
    
    def __init__(self, lines):
        self.lines = lines

    def __str__(self):
        return "\n".join([str(line) for line in self.lines])

    def __repr__(self):
        return "<Stanza: {}>".format(self.lines[0])

    def __iter__(self):
        return (line for line in self.lines)
        
    
class Line:
    '''A line of verse.
    '''
    def __init__(self, line):
        self.line = line            # the text of the line
        self.rhyme_group = ""       # where we're at in the rhyme scheme

    def tail(self):
        '''Return the "last part" of the line. For now, this is
        just the last word. Probably 
        '''
        return 

    def __str__(self):
        return self.line

    def __repr__(self):
        return "<Line: {}>".format(self.line)


sample_lines = """
          Loveliest of trees, the cherry now
          Is hung with bloom along the bough,
          And stands about the woodland ride
          Wearing white for Eastertide.

          Now, of my threescore years and ten,
          Twenty will not come again,
          And take from seventy springs a score,
          It only leaves me fifty more.

          And since to look at things in bloom
          Fifty springs are little room,
          About the woodlands I will go
          To see the cherry hung with snow.""".split("\n")

def strip_lines(lines):
    '''Delete leading and trailing lines which are empty except for 
    possible whitespace
    Note: destructive function, acts directly on its target
    '''
    while not lines[0].strip():
        lines.pop(0)
    while not lines[-1].strip():
        lines.pop(-1)
