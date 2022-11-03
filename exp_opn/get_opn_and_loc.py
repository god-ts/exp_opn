from dep_syn import Dep_Syn
from get_ner_loc import NER_All_Loc
import re
import fasttext


class Get_Opn_and_Loc:
    def __init__(self, sentiment_model):
        self.nal = NER_All_Loc()
        self.ds = Dep_Syn()
        self.model = fasttext.load_model(sentiment_model)

    def split_sentence(self, text: str):
        text_list = [i for i in re.split(r'[.:?!\n\t]', text) if i.strip() != '' and len(i.strip().split()) >= 2]
        return text_list

    def get_sentiment(self, text):
        text = text.lower()
        result = self.model.predict(text)
        return result[0][0][9:]

    def get_opn_and_loc(self, text: str):
        text = text.lower()
        text_list = self.split_sentence(text)
        opns = []
        for t in text_list:
            opns.extend(self.ds.get_opn(t))
        opn_locs = []
        for opn in opns:
            opn_loc = []
            noun_target = []
            for n in opn:
                for o in n.split():
                    noun_target.append(o)
                    token_locs = self.nal.get_ner_loc(text, [o])
                    if token_locs:
                        try:
                            token_loc = token_locs[noun_target.count(o) - 1]
                        except:
                            token_loc = token_locs[0]
                        opn_loc.append(token_loc)
            opn_locs.append(opn_loc)
        return opns, opn_locs

    def show_opn(self, text):
        version = 'v1'
        list_opn = []
        try:
            dep_syn = self.get_opn_and_loc(text)
        except:
            print('获取观点异常')
            return list_opn
        for opn, loc in zip(dep_syn[0], dep_syn[1]):
            show_text_list = []
            show_loc_list = []
            dic_opn = {}
            for o in opn:
                show_text_list.extend([x for x in o.split()])
            for l in loc:
                show_loc_list.append(l)
            dic_opn['opn_words'] = show_text_list
            dic_opn['opn_position'] = show_loc_list
            dic_opn['sentiment'] = self.get_sentiment(" ".join(show_text_list))
            dic_opn['version'] = version
            list_opn.append(dic_opn)
        return list_opn





if __name__ == '__main__':
    gol = Get_Opn_and_Loc('sentiment/model_opn_sentiment_0923.bin')
    print(gol.show_opn("""after 6 hours of driving it's still not close to freezing
    being a woman it's extremely troubling and unexpected, especially as it's at the very front and runs down half way to the back of my head."""))
