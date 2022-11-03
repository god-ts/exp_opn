from get_ner_loc import NER_All_Loc
from nearby_loc import Nearby_Loc

nl = Nearby_Loc()
nal = NER_All_Loc()

def get_sorted_opn3(text: str, opn: str):
    loc_list = []
    opn_list = []
    for o in opn.split():
        loc_list.append(nal.get_ner_loc(text, [o]))
        # print(nal.get_ner_loc(text, [o]))
    try:
        loc_list.sort(key=lambda x: int(str(x[0]).split(',')[0]))
        for loc in loc_list:
            l = loc[0].split(',')
            opn_list.append(text[int(l[0]):int(l[1])])
        return " ".join(opn_list)
    except:
        return opn

def get_sorted_opn2(text: str, ner: str, opn: str):
    loc_list = []
    opn_list = []
    ner_loc = nal.get_ner_loc(text, [ner])
    opinion = [opn.split()]
    # word_loc = nl.get_word_loc(text, opinion, ner_loc)
    for o in opn.split():
        loc_list.extend(nl.get_word_loc(text, [[o]], ner_loc))
        # print(loc_list)
    try:
        loc_list.sort(key=lambda x: x[0])
        for loc in loc_list:
            opn_list.append(text[loc[0]:loc[1]])
        return " ".join(opn_list)
    except Exception as e:
        print(e)
        return opn


def get_sorted_opn(text: str, opn: str):
    all_loc_list = []
    opn_list = []
    for o in opn.split():
        all_loc_list.append(nal.get_ner_loc(text, [o]))
        # print(nal.get_ner_loc(text, [o]))
    l_list = []
    loc_list = []
    for loc in all_loc_list:
        for l in loc:
            if l[0] not in l_list:
                loc_list.append(l)
                l_list.append(l[0])
                break
    try:
        # loc_list.sort(key=lambda x: int(str(x[0]).split(',')[0]))
        loc_list.sort(key=lambda x: int(x[0]))
        # loc_list.sort(key=lambda x: int(str(x).split(',')[0]))
        for loc in loc_list:
            opn_list.append(text[int(loc[0]):int(loc[1])])
        return " ".join(opn_list)
    except Exception as e:
        print("!!!!!! get_sorted_opn error !!!!!!:", e)
        return opn


if __name__ == '__main__':

    # text = 'this product didn’t work at all'
    # opn = 'at all work'
    text = "after 6 still hours of driving it's still not close to freezing"
    ner = 'it'
    opn = "freezing to close not still after hours"

    print(get_sorted_opn(text, opn))
    # print(get_sorted_opn2(text, ner, opn))
    # print(get_sorted_opn3(text, opn))
    # loc_list = []
    # for o in opn.split():
    #     # print(nal.get_ner_loc(text, [o]))
    #     loc_list.append(nal.get_ner_loc(text, [o]))
    #
    #
    # print(loc_list)
    # loc_list.sort(key=lambda x: int(str(x[0]).split(',')[0]))
    # print(loc_list)
    # opn_list = []
    # for loc in loc_list:
    #     l = loc[0].split(',')
    #     opn_list.append(text[int(l[0]):int(l[1])])
    #
    # print(" ".join(opn_list))
