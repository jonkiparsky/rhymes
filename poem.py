from itertools import chain
from functools import reduce

from rhymes import (
    read_cmu_dict,
    analyze_rhyme
    )

from render import render_results

WORD_KEYS, _  = read_cmu_dict()

class Poem:
    def __init__(self, lines, title="", has_header=True):
        self.stanzas = []
        self.read_lines(lines)
        self.title = title or lines[0]
        if(has_header):
            self.remove_header()  
                                  
    def read_lines(self, lines):
        strip_lines(lines)
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

    def render_html(self):
        fname = "output.html"
        filepath = r"output/{}".format(fname)
        stanzas = [stanza.prep_html() for stanza in self.stanzas]
        f = open (filepath, "w")
        f.write(render_results(title=self.title,
                               stanzas=stanzas))

    def remove_header(self, threshhold=2):
        '''Attempt to remove title and other preceding data, like a date. 
        Current criteria for header (must meet all to be stripped):
            - supplied stanzas differ in length
            - any single-line stanza that occurs before the first stanza with 
            $threshhold or more lines
        Known bug: if a poem starts with a single line stanza, this will 
        incorrectly remove it.
        '''
        stanza_lengths = [len(stanza) for stanza in self.stanzas]

        # if all stanzas are the same length, we have no hope of figuring
        # out what the header is. Abort!

        if(min(stanza_lengths) == max(stanza_lengths)): return
        
        delete_from = 0
        for index, stanza_len in enumerate(stanza_lengths): 
            if stanza_len >= threshhold:
                break
            elif stanza_len == 1:
                delete_from = index + 1

        self.stanzas = self.stanzas[delete_from:]
      

    def __str__(self):
        return "\n\n".join([str(stanza) for stanza in self.stanzas])

    def __repr__(self):
        identifier = self.title
        return "<Poem: {}>".format(self.title)

    def __iter__(self):
        return (line for line in chain(*self.stanzas))

    def __len__(self):
        return sum([len(stanza) for stanza in self.stanzas])
       
      

        
    
class Stanza:
    '''A section of a poem/song/metrical whatnot.
    Assume for the nonce that empty lines separate stanzas. 
    '''
    
    def analyze(self):
        return analyze_rhyme([str(line) for line in self.lines], WORD_KEYS)

    def prep_html(self):
        classes = self.analyze()
        lines = [(line[0:line.rindex(' ')],
                 line[line.rindex(' '):],
                 f"group-{cls}")
                for line, cls in zip(map(str, self.lines), classes)]
        return lines
                

    
    def __init__(self, lines):
        self.lines = lines

    def __str__(self):
        return "\n".join([str(line) for line in self.lines])

    def __repr__(self):
        return f"<Stanza: {self.lines[0]}>"

    def __iter__(self):
        return (line for line in self.lines)

    def __len__(self):
        return len(self.lines)
        
    
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


