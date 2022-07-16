import validators
class Parser():

    #Initialize Parser
    def __init__(self, raw_textie, category="note", textie="", errors = []):
        self.raw_textie = raw_textie
        self.category = category
        self.textie = textie
        self.errors = errors 
        self.parse(self.raw_textie)

    #Add error
    def set_error(self, error):
        self.errors.append(error)

    #Parse raw textie on initialization
    def parse(self, raw_textie):
        if len(raw_textie)<1:
            self.set_error("Textie is empty")

        #Check if textie is a link
        if self.is_url(self.raw_textie) == True:
            self.category = "url"
            return

        #Check if textie has a type
        if ":" in raw_textie:
            split_textie=raw_textie.split(":")
            self.category = split_textie[0]
            self.textie = split_textie[1]
        else:
            self.textie = raw_textie

    #Check if textie is a url
    def is_url(self, raw_textie):
        return validators.url(raw_textie)
        


            
