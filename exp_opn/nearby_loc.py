import re

class Nearby_Loc:
    def get_word_loc(self, text, opinion_words, target_loc):
        pos_lists = []
        for words in opinion_words:
            try:
                opinion_word = ' '.join(words)
                left = int(target_loc[0].split(',')[0])
                # right = int(loc[0].split(',')[1])
                text = str(text).lower()
                loc = self.get_keyword_loc(text, opinion_word)
                pos_list = []
                while loc:
                    pos_list.append(loc)
                    loc = self.get_keyword_loc(text[loc[1]:], opinion_word, start_pos=loc[1])
                distence = float('inf')
                last_pos = pos_list[0]
                for p in pos_list:
                    p_left = int(p[0])
                    # p_right = int(p[1])
                    if abs(p_left - left) <= distence:
                        distence = abs(p_left - left)
                        last_pos = p
                pos_lists.append(last_pos)
            except:
                pos_lists.append([0, 0])
                continue
        return pos_lists

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

    # text = """I don't know where to begin. I read a lot of review saying that these pant runs small. So I want up a size. (12 regular) Nope LIES!!! There is nothing small about this pants. These pants sits past my bellybutton, the are extremely long, and the bottom of these pants are bell dottom. They are not nothing like the picture. Snice everything is closed right, I will be ordering again in the right size, in hopes of a different story.
    # """
    #
    # opinion = [['bottom'], ['pants'], ['bell', 'dottom']]
    # target_loc = ['255,260']


    text = """I purchased a   53 QT refrigerator from Amazon.   We received it on May 2nd 2021.  This item is to be used on a trip that we have scheduled for June 26th of 2021.  We wanted to check the item to make sure it functioned properly.  We left the unit set for about 5 days, we then plugged it in to our wall outlet using the supplied adapter that came with the unit.  The unit initially worked well and cooled down to freezing, however after about 12 hours of use with the 110 adapter, the unit began to show the E4 error code.  I unplugged the unit and let it sit, I tried lowering the temperature to no avail.  The unit will start and run for about two or three seconds then show the E4 error code again.  This unit is brand new running for less than 48 hours and has only had a six pack of soda and a glass of water in it, testing the temperature.  I would like a replacement shipped to me to resolve this issue.  As I stated, we have a cross country trip planned for the end of June and need this unit for that trip.  I look forward to hearing from you on this matter, thank you."""

    opinion = [['new', 'running', 'for', 'less', 'than', '48', 'hours'], ['has', 'only'], ['a'], ['dskfa']]
    target_loc = ['708,712']
    opinion_loc = Nearby_Loc().get_word_loc(text, opinion, target_loc)
    print(opinion_loc)

    for loc in opinion_loc:
        print(text[loc[0]:loc[1]])

    # a = [1, 2]
    # b = ",".join([str(i) for i in a])
    # print(a)
    # print(b)


# import pandas as pd
#
# df = pd.read_csv('data/f.csv', nrows=20)
#
#
# lines = []
# for _, row in df.iterrows():
#     text = row['text']
#     opinions = eval(row['opn'])
#     target_loc = eval(row['loc'])
#     opinion_loc = get_word_loc(text, opinions, target_loc)
#     # print(opinion_loc)
#     # for loc in opinion_loc:
#     #     print(text[loc[0]:loc[1]])
#     lines.append([row[1], row[2], row[3], row[4], row[5], opinion_loc])
# print(lines)



