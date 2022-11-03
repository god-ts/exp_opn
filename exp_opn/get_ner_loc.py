import re


class NER_All_Loc:
    def get_ner_loc(self, text: str, ner_words: list):
        loc_list = []
        for word in ner_words:
            try:
                text = str(text).lower()
                loc = self.get_keyword_loc(text, word)
                while loc:
                    loc_list.append([loc[0], loc[1]])
                    loc = self.get_keyword_loc(text[loc[1]:], word, start_pos=loc[1])
                if not loc:
                    if word in text:
                        left = text.find(word)
                        right = left + len(word)
                        if not loc_list:
                            loc_list.append([left, right])
                    else:
                        loc_list.append([0, 0])
            except:
                continue
        return loc_list

    def get_keyword_loc(self, text, keyword, start_pos=0):
        text = str(text).lower()
        pattern = f'[^a-zA-Z]({keyword})[^a-zA-Z]|^({keyword})[^a-zA-Z]|[^a-zA-Z]({keyword})$'
        match_keyword = re.search(pattern, text)
        if match_keyword:
            loc = match_keyword.span()
            left = loc[0]
            right = loc[1]
            if left != 0 or not match_keyword.group()[0].isalpha():
                left = left + 1
            if right != len(text) or not match_keyword.group()[-1].isalpha():
                right = right - 1
            return [start_pos + left, start_pos + right]
        return




if __name__ == '__main__':

    # text = "My units co units. trol panel is no longer working, I can't adjust temperature or turn it off, it's a maximum coldness please let me knkw how we can get this taken care of units. units."
    # nal = NER_All_Loc()
    # p = nal.get_ner_loc(text, ['units'])
    # print(p)

    nal = NER_All_Loc()
    text = "it's running all the time which makes both of my products unreliable"
    print(nal.get_ner_loc(text, ["it"]))









