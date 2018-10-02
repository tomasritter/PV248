class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        s = "Print Number: " + str(self.print_id) + "\n"
        s += "Composer: "
        # Go through each compsoer in the list
        for i in range(len(self.edition.composition.authors)):
            c = self.edition.composition.authors[i]
            # Add name to the output string
            s += c.name
            # Add year of birth/death if present
            if not c.born is None or not c.died is None:
                s += " (" + (str(c.born) if not c.born is None else "")
                s += "--" + (str(c.died) if not c.died is None else "") + ")"
            # Add "; " behind all names except for the last one
            if i != len(self.edition.composition.authors) - 1:
                s += "; "
        s += "\n"
        s += "Title: " + (self.edition.composition.name or "") + "\n"
        s += "Genre: " + (self.edition.composition.genre or "") + "\n"
        s += "Key: " + (self.edition.composition.key or "") + "\n"
        s += "Composition Year: " + (self.edition.composition.year or "") + "\n"
        s += "Edition: " + (self.edition.name or "") + "\n"
        s += "Editor: "
        for i in range(len(self.edition.authors)):
            c = self.edition.authors[i]
            s += c.name
            # Add ", " behind all names except for the last one
            if i != len(self.edition.authors) - 1:
                s += ", "
        s += "\n"
        # Add voices to the output string
        for i in range(len(self.edition.composition.voices)):
            v = self.edition.composition.voices[i]
            # Uses index + 1 to get the original order of Voice lines
            s += "Voice " + str(i + 1) + ": "
            if v.range is None: 
                s += v.name or ""
            elif v.name is None:
                s += v.range
            else:
                s += v.range + ", " + v.name
            s += "\n"
        s += "Partiture: " + ("yes" if self.partiture else "no") + "\n"
        s += "Incipit: " + (self.edition.composition.incipit if not self.edition.composition.incipit is None else "") + "\n"
        return s
        
    def composition(self):
        return self.edition.composition

class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name

class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died


