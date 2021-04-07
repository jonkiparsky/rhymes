class Poem:
    def __init__(self, lines, title=""):
        self.read_lines(lines)
        self.title = title or self.stanzas[0].lines[0]

    def read_lines(self, lines):
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

    def __str__(self):
        return "\n\n".join([str(stanza) for stanza in self.stanzas])

    def __repr__(self):
        identifier = self.title
        return "<Poem: {}>".format(self.title)
            
class Stanza:
    '''A section of a poem/song/metrical whatnot.
    Assume for the nonce that empty lines separate stanzas. 
    '''
    def __init__(self, lines):
        self.lines = lines

    def __str__(self):
        return "\n".join([str(line) for line in self.lines])

    def __repr__(self):
        return "<Stanza: {}>".format(self.lines[0])

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
