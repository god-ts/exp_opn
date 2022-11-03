import spacy
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import sort_opn
# from get_ner_loc import NER_All_Loc

class Dep_Syn:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        # self.nal = NER_All_Loc()
        self.nlp = spacy.load("en_core_web_sm/en_core_web_sm-3.4.0")
        # self.nlp = spacy.load("en_core_web_trf/en_core_web_trf-3.4.0")
        self.stop_words = ['am', 'is', 'are', 'was', 'were', "'s", "'m", "'re"]
        self.stop_opn = ['', 'same', 'new', 'black', 'last', 'so', 'at all', 'sent', 'where', 'what', 'green',
                         'want', 'have', 'why', 'android', 'all', 'red', 'also', 'as', 'anything', 'be', 'still'
                         '’s', "'s", '’m', 'has', 'here', 'just', 'product', 'looked', 'next', 'take', 'pretty',
                         'runs', 'looks', 'says', 'made', 'did', 'blue', 'as', 'had', 'something', 'other', 'buy',
                         'only', 'came', 'get', 'to', 'total', 'white', 'purchased', 'which', 'first', 'second',
                         'third', 'way', 'look', 'very', 'half', 'full']
        self.pronouns = ['it', 'its', 'they', 'item']

    def get_all_nodes(self, word: str):
        word = self.lemmatizer.lemmatize(word, pos='n')
        node_list = []
        for w in wn.synsets(word):
            # if w.pos() == 'n' and w._name.split('.')[0] == word:
            if w.pos() == 'n':
                path = w.hypernym_paths()
                for p in path:
                    for syn in p:
                        node_list.append(syn.name().split('.')[0])
        return list(set(node_list))

    def get_noun_list(self, text):
        text = str(text).lower()
        doc = self.nlp(text)
        noun_node_list = ['artifact', 'physical_property', 'unit_of_measurement', 'quality', 'material', 'unit']
        noun_list = []
        for t in doc:
            if t.tag_ in ['NN', 'NNS'] and len(t.text) > 1 and str(t.text).encode('utf-8').isalpha():
                word = self.lemmatizer.lemmatize(t.text, pos='n')
                all_nodes = self.get_all_nodes(word)
                for noun_node in noun_node_list:
                    if noun_node in all_nodes:
                        noun_list.append(t.text)
                        break
        return list(set(noun_list))

    def get_opn(self, text):
        doc = self.nlp(text.lower())
        noun_list = self.get_noun_list(text)
        opns = []
        # opn_locs = []
        for token in doc:
            noun = []
            opn = []
            neg = []
            current_noun = ''
            current_neg = ''
            if token.pos_ in ['VERB', 'AUX']:
                if not [child for child in token.children if child.dep_ in ['nsubj', 'nsubjpass'] and (
                        (child.pos_ in ['NOUN'] and child.text in noun_list) or child.text in self.pronouns)]:
                    continue
                # 代词做主语,后面跟状语从句(advcl),忽略
                if [i for i in token.children if i.text in self.pronouns] and set([i.dep_ for i in token.children]) >= {
                    'nsubj', 'advcl'}:
                    continue
                if token.pos_ in ['VERB']:
                    if token.has_head() and token.dep_ in ['ccomp', 'advcl']:
                        if not [child for child in token.children if child.dep_ in ['nsubj', 'nsubjpass'] and (
                                (child.pos_ in ['NOUN'] and child.text in noun_list) or child.text in self.pronouns)]:
                            continue
                        for a_token in token.head.children:
                            if a_token.dep_ in ['neg'] or a_token.text in ['no']:
                                neg.append([token.text, a_token.text])
                                current_neg = ''
                    opn.append([token.text, current_noun])
                for child in token.children:
                    if child.dep_ in ['nsubj', 'nsubjpass'] and (
                            (child.pos_ in ['NOUN'] and child.text in noun_list) or child.text in self.pronouns):
                        current_noun = child.text
                        noun.append(current_noun)
                        for n_child in child.children:
                            if n_child.dep_ in ['neg'] or n_child.text in ['no']:
                                neg.append([child.head.text, n_child.text])
                                current_neg = ''
                            if n_child.dep_ in ['conj']:
                                current_noun = n_child.text
                                noun.append(current_noun)
                            if n_child.dep_ in ['compound']:
                                noun[-1] = n_child.text + " " + noun[-1]
                                current_noun = noun[-1]
                                for n_child2 in n_child.children:
                                    noun[-1] = n_child2.text + " " + noun[-1]
                                    current_noun = noun[-1]
                    elif child.dep_ in ['nsubj', 'nsubjpass'] and child.pos_ in ['PRON'] and child.text not in self.pronouns:
                        opn = opn[0:-1]
                        break
                    elif child.dep_ in ['neg'] or child.text in ['no']:
                        neg.append([child.head.text, child.text])
                        current_neg = child.text
                        if child.head.pos_ in ['AUX']:
                            if opn:
                                opn[-1][0] = child.text + ' ' + opn[-1][0]
                            else:
                                opn.append([child.head.text, current_noun])
                        for n_child in child.children:
                            if n_child.dep_ in ['neg'] or n_child.text in ['no']:
                                neg.append([n_child.head.text, n_child.text])
                                current_neg = n_child.text
                    elif child.dep_ in ['amod', 'advmod', 'xcomp', 'acomp', 'attr', 'conj', 'dobj', 'ccomp', 'relcl',
                                        'oprd', 'advcl', 'oprd']:
                        # if child.pos_ in ['ADV', 'ADP']:
                        if child.pos_ in ['PRON', 'PROPN'] and child.text not in self.pronouns:
                            opn = opn[0:-1]
                            break
                        if child.dep_ in ['ccomp']:
                            if [c_child.text for c_child in child.children if
                                (c_child.dep_ in ['nsubj', 'nsubjpass'] and c_child.pos_ in ['PRON'])]:
                                continue
                            else:
                                for c_child in child.children:
                                    if c_child.dep_ in ['neg'] or c_child.text in ['no']:
                                        neg.append([c_child.head.text, c_child.text])
                                        current_neg = ''
                                if current_neg:
                                    neg.append([child.text, current_neg])
                                    current_neg = ''
                        if child.pos_ in ['AUX'] and not [i for i in child.children if i.dep_ in ['acomp']]:
                            continue
                        if child.dep_ in ['conj']:
                            if [c_child.text for c_child in child.children if
                                (c_child.dep_ in ['nsubj', 'nsubjpass'] and c_child.pos_ in ['PRON'])]:
                                continue
                            if child.pos_ in ['VERB', 'ADJ']:
                                if [c_child for c_child in child.children if
                                    c_child.dep_ in ['nsubj', 'nsubjpass'] and ((c_child.pos_ in [
                                        'NOUN'] and c_child.text in noun_list) or c_child.text in self.pronouns)]:
                                    continue
                                opn.append([child.text, current_noun])
                                for n_child in child.children:
                                    if n_child.dep_ in ['neg'] or n_child.text in ['no']:
                                        neg.append([n_child.head.text, n_child.text])
                                        current_neg = ''
                                if current_neg:
                                    neg.append([child.text, current_neg])
                                    current_neg = ''
                            elif (child.pos_ in ['NOUN'] and child.text in noun_list) or child.text in self.pronouns:
                                current_noun = child.text
                                noun.append(current_noun)
                            for c_child in child.children:
                                if c_child.dep_ in ['nsubj', 'nsubjpass'] and ((c_child.pos_ in [
                                    'NOUN'] and c_child.text in noun_list) or c_child.text in self.pronouns):
                                    current_noun = c_child.text
                                    noun.append(current_noun)
                                    for a_child in c_child.children:
                                        if a_child.dep_ in ['amod', 'advmod']:
                                            opn.append([a_child.text, current_noun])
                                elif c_child.pos_ in ['VERB']:
                                    if c_child.dep_ in ['advcl']:
                                        # pass
                                        if opn:
                                            opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                        else:
                                            opn.append([c_child.text, current_noun])
                                        # opn.append([c_child.text, current_noun])
                                        for d_child in c_child.children:
                                            if d_child.dep_ in ['ccomp', 'xcomp', 'mark']:
                                                if opn:
                                                    opn[-1][0] = d_child.text + ' ' + opn[-1][0]
                                                else:
                                                    opn.append([d_child.text, current_noun])
                                                for e_child in d_child.children:
                                                    if e_child.dep_ in ['ccomp', 'xcomp']:
                                                        if opn:
                                                            opn[-1][0] = e_child.text + ' ' + opn[-1][0]
                                                        else:
                                                            opn.append([e_child.text, current_noun])
                                    elif c_child.dep_ in ['ccomp', 'xcomp']:
                                        if opn:
                                            opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                        else:
                                            opn.append([c_child.text, current_noun])
                                        for d_child in c_child.children:
                                            if d_child.dep_ in ['dobj']:
                                                if opn:
                                                    opn[-1][0] = d_child.text + ' ' + opn[-1][0]
                                                else:
                                                    opn.append([d_child.text, current_noun])
                                                for e_child in d_child.children:
                                                    if e_child.dep_ in ['nummod']:
                                                        if opn:
                                                            opn[-1][0] = e_child.text + ' ' + opn[-1][0]
                                                        else:
                                                            opn.append([e_child.text, current_noun])
                                    else:
                                        opn.append([c_child.text, current_noun])
                                        for d_child in c_child.children:
                                            if d_child.dep_ in ['xcomp']:
                                                if opn:
                                                    opn[-1][0] = d_child.text + ' ' + opn[-1][0]
                                                else:
                                                    opn.append([d_child.text, current_noun])
                                    for n_child in c_child.children:
                                        if n_child.dep_ in ['neg'] or n_child.text in ['no']:
                                            neg.append([n_child.head.text, n_child.text])
                                        if n_child.dep_ in ['advmod', 'prt', 'amod']:
                                            if opn:
                                                opn[-1][0] = n_child.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([n_child.text, current_noun])
                                elif c_child.dep_ in ['dobj', 'oprd']:
                                    if opn:
                                        opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                    else:
                                        opn.append([c_child.text, current_noun])
                                    for d_child in c_child.children:
                                        if d_child.dep_ in ['compound', 'advmod', 'amod', 'nummod']:
                                            if opn:
                                                opn[-1][0] = d_child.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([d_child.text, current_noun])
                                elif c_child.dep_ in ['advmod']:
                                    if c_child.pos_ in ['ADV']:
                                        if c_child.text not in ['so']:
                                            if opn:
                                                opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([c_child.text, current_noun])
                                    else:
                                        opn.append([c_child.text, current_noun])
                                    for n_child in c_child.children:
                                        if n_child.dep_ in ['neg'] or n_child.text in ['no']:
                                            neg.append([n_child.head.text, n_child.text])
                                elif c_child.dep_ in ['acomp']:
                                    if opn:
                                        opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                        if len(opn) >= 2:
                                            opn[-2][0] = c_child.text + ' ' + opn[-2][0]
                                    else:
                                        opn.append([c_child.text, current_noun])
                                    for d_child in c_child.children:
                                        if d_child.dep_ in ['compound', 'advmod', 'amod']:
                                            if opn:
                                                opn[-1][0] = d_child.text + ' ' + opn[-1][0]
                                                if len(opn) >= 2:
                                                    opn[-2][0] = d_child.text + ' ' + opn[-2][0]
                                            else:
                                                opn.append([d_child.text, current_noun])
                        else:
                            if child.dep_ in ['advcl']:
                                opn.append([child.text, current_noun])
                            else:
                                if opn:
                                    opn[-1][0] = child.text + ' ' + opn[-1][0]
                                else:
                                    opn.append([child.text, current_noun])
                            for o_child in child.children:
                                if o_child.dep_ in ['nsubj', 'nsubjpass'] and o_child.pos_ not in ['PRON']:
                                    if opn:
                                        opn[-1][0] = o_child.text + ' ' + opn[-1][0]
                                    else:
                                        opn.append([o_child.head.text, current_noun])
                                    for a_child in o_child.children:
                                        if a_child.dep_ in ['compound']:
                                            if opn:
                                                opn[-1][0] = a_child.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([a_child.head.text, current_noun])
                                            for b_child in a_child.children:
                                                if opn:
                                                    opn[-1][0] = b_child.text + ' ' + opn[-1][0]
                                                else:
                                                    opn.append([b_child.head.text, current_noun])
                                elif o_child.dep_ in ['neg'] or o_child.text in ['no']:
                                    neg.append([o_child.head.text, o_child.text])
                                    current_neg = ''
                                    for n_child in o_child.children:
                                        if n_child.dep_ in ['neg'] or n_child.text in ['no']:
                                            neg.append([n_child.head.text, n_child.text])
                                            current_neg = ''
                                elif o_child.dep_ in ['advmod', 'npadvmod', 'amod', 'prt', 'acomp', 'nummod']:
                                    if opn:
                                        opn[-1][0] = o_child.text + ' ' + opn[-1][0]
                                    else:
                                        opn.append([o_child.text, current_noun])
                                    for a_child in o_child.children:
                                        if a_child.dep_ in ['advmod', 'adjmod', 'amod']:
                                            if opn:
                                                opn[-1][0] = a_child.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([a_child.text, current_noun])
                                        if a_child.dep_ in ['neg'] or a_child.text in ['no']:
                                            neg.append([a_child.head.text, a_child.text])
                                            current_neg = ''
                                elif o_child.dep_ in ['conj']:
                                    opn.append([o_child.text, current_noun])
                                    opn[-1][0] = o_child.head.head.text + ' ' + opn[-1][0]
                                    for o_child2 in o_child.children:
                                        if o_child2.dep_ in ['advmod', 'npadvmod', 'amod', 'acomp']:
                                            if opn:
                                                opn[-1][0] = o_child2.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([o_child2.text, current_noun])
                                        if o_child2.dep_ in ['neg'] or o_child.text in ['no']:
                                            neg.append([o_child2.head.text, o_child2.text])
                                            current_neg = ''
                                        for b_child in o_child2.children:
                                            if b_child.dep_ in ['advmod']:
                                                if opn:
                                                    opn[-1][0] = b_child.text + ' ' + opn[-1][0]
                                                else:
                                                    opn.append([b_child.text, current_noun])
                                    if current_neg:
                                        neg.append([o_child.text, current_neg])
                                        current_neg = ''
                                elif o_child.dep_ in ['compound']:
                                    if opn:
                                        opn[-1][0] = o_child.text + ' ' + opn[-1][0]
                                    else:
                                        opn.append([o_child.text, current_noun])
                                    for a_child in o_child.children:
                                        if a_child.dep_ in ['amod']:
                                            if opn:
                                                opn[-1][0] = a_child.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([a_child.text, current_noun])
                                elif o_child.dep_ in ['dobj', 'prep', 'pobj']:
                                    if opn:
                                        opn[-1][0] = o_child.text + ' ' + opn[-1][0]
                                    else:
                                        opn.append([o_child.text, current_noun])
                                    for d_child in o_child.children:
                                        if d_child.dep_ in ['compound', 'advmod', 'amod', 'pobj', 'pcomp', 'nummod',
                                                            'relcl']:
                                            if opn:
                                                opn[-1][0] = d_child.text + ' ' + opn[-1][0]
                                            else:
                                                opn.append([d_child.text, current_noun])
                                            for e_child in d_child.children:
                                                if e_child.dep_ in ['compound', 'advmod', 'amod', 'pobj', 'pcomp',
                                                                    'nummod', 'relcl']:
                                                    if opn:
                                                        opn[-1][0] = e_child.text + ' ' + opn[-1][0]
                                                    else:
                                                        opn.append([e_child.text, current_noun])
                            # if current_neg:
                            #     neg.append([child.text, current_neg])
                            #     current_neg = ''
                    elif child.dep_ in ['prt', 'prep']:
                        if opn:
                            opn[-1][0] = opn[-1][0] + " " + child.text
                        else:
                            opn.append([child.text, current_noun])
                        for c_child in child.children:
                            if c_child.dep_ in ['pobj', 'prep']:
                                if opn:
                                    opn[-1][0] = opn[-1][0] + " " + c_child.text
                                else:
                                    opn.append([c_child.text, current_noun])
                                for d_child in c_child.children:
                                    if d_child.dep_ in ['compound', 'amod', 'pobj', 'relcl']:
                                        if opn:
                                            opn[-1][0] = opn[-1][0] + " " + d_child.text
                                        else:
                                            opn.append([d_child.text, current_noun])
                                        for e_child in d_child.children:
                                            if e_child.dep_ in ['compound', 'amod', 'pobj', 'relcl', 'advmod']:
                                                if opn:
                                                    opn[-1][0] = opn[-1][0] + " " + e_child.text
                                                else:
                                                    opn.append([e_child.text, current_noun])

            elif token.pos_ in ['NOUN'] and token.text in noun_list:
                if token.has_head() and token.dep_ in ['pobj', 'compound']:
                    continue
                current_noun = token.text
                noun.append(current_noun)
                for child in token.children:
                    if child.dep_ in ['compound']:
                        noun[-1] = child.text + " " + noun[-1]
                        current_noun = noun[-1]
                        for n_child in child.children:
                            if n_child.dep_ in ['compound']:
                                noun[-1] = n_child.text + " " + noun[-1]
                                current_noun = noun[-1]
                    elif child.dep_ in ['conj'] and child.pos_ not in ['VERB']:
                        current_noun = child.text
                        noun.append(current_noun)
                        for o_child in child.children:
                            if o_child.dep_ in ['amod']:
                                opn.append([o_child.text, current_noun])
                    elif child.dep_ in ['neg'] or child.text in ['no']:
                        neg.append([child.head.text, child.text])
                        current_neg = child.text
                        for n_child in child.children:
                            if n_child.dep_ in ['neg'] or n_child.text in ['no']:
                                neg.append([n_child.head.text, n_child.text])
                                current_neg = ''
                    elif child.dep_ in ['amod']:
                        opn.append([child.text, current_noun])
                        for c_child in child.children:
                            if c_child.dep_ in ['advmod']:
                                if opn:
                                    opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                else:
                                    opn.append([c_child.text, current_noun])
                    elif child.dep_ in ['relcl']:
                        if child.pos_ in ['VERB']:
                            continue
                        if opn:
                            opn[-1][0] = child.text + ' ' + opn[-1][0]
                        else:
                            opn.append([child.text, current_noun])
                        for c_child in child.children:
                            # if c_child.pos_ in ['PRON', 'PROPN'] and c_child.text not in pronouns:
                            #     break
                            if c_child.pos_ in ['PRON', 'PROPN']:
                                if opn:
                                    opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                else:
                                    opn.append([c_child.text, current_noun])
                            if c_child.dep_ in ['neg'] or c_child.text in ['no']:
                                neg.append([c_child.head.text, c_child.text])
                            if c_child.dep_ in ['advmod', 'compound', 'amod', 'dobj', 'acomp']:
                                if opn:
                                    opn[-1][0] = c_child.text + ' ' + opn[-1][0]
                                else:
                                    opn.append([c_child.text, current_noun])
                                for d_child in c_child.children:
                                    if d_child.dep_ in ['compound', 'advmod', 'amod', 'acl', 'nummod']:
                                        if opn:
                                            opn[-1][0] = d_child.text + ' ' + opn[-1][0]
                                        else:
                                            opn.append([d_child.text, current_noun])
                        if current_neg:
                            neg.append([child.text, current_neg])
                            current_neg = ''
            if noun:
                # print(token.text)
                # print(noun)
                # print(neg)
                # print(opn)
                #
                together = []
                remove_opn = []
                for n in noun:
                    for o in opn:
                        if o[1] == '' or o[1] == n:
                            has_neg = False
                            for ne in neg:
                                if ne[0] in o[0].split():
                                    without_stop_words = []
                                    for w in o[0].split():
                                        if w not in self.stop_words:
                                            without_stop_words.append(w)
                                    opinion = " ".join(without_stop_words)
                                    together.append([n, ne[1], opinion])
                                    remove_opn = [o[0], o[1]]
                                    has_neg = True
                                    break
                            if has_neg == False:
                                without_stop_words = []
                                for w in o[0].split():
                                    if w not in self.stop_words:
                                        without_stop_words.append(w)
                                opinion = " ".join(without_stop_words)
                                together.append([n, "", opinion])
                                remove_opn = [o[0], o[1]]
                    if remove_opn in opn:
                        opn.remove(remove_opn)
                if together:
                    for words in together:
                        if not words[2].strip().replace(' ', '').encode('utf-8').isalpha():
                            continue
                        if words[2].strip() not in self.stop_opn:
                            o = [words[0], words[1], sort_opn.get_sorted_opn(doc.text, words[2])]
                            if o not in opns:
                                opns.append(o)
        return opns
        # print(opns)
        # for opn in opns:
        #     opn_loc = []
        #     noun_target = []
        #     for n in opn:
        #         for o in n.split():
        #             noun_target.append(o)
        #             token_locs = self.nal.get_ner_loc(doc.text, [o])
        #             if token_locs:
        #                 token_loc = token_locs[noun_target.count(o) - 1]
        #                 opn_loc.append(token_loc)
        #     opn_locs.append(opn_loc)
        # return opns, opn_locs
        # return [i for i in opns if opns.count(i) == 1]



if __name__ == '__main__':
    ds = Dep_Syn()
    # print(ds.get_opn("i would like a refund please as the quality is not as advertised"))
    # print(ds.get_opn("being a woman it's extremely troubling and unexpected, especially as it's at the very front and runs down half way to the back of my head."))
    print(ds.get_opn("""after 6 hours of driving it's still not close to freezing"""))
    print(ds.get_opn("""While socks are well-made, crossover bands are cute and grips on soles provided some stability during Pilates class, they are NOT “one size fits all” and too big for my size 7 feet to use during workout. Socks moved around way too much during class, even after washing and drying completely in dryer."""))
    # print(ds.get_opn("""it's not good"""))
