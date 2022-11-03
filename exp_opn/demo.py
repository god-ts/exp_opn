from get_opn_and_loc import Get_Opn_and_Loc


if __name__ == '__main__':
    gol = Get_Opn_and_Loc('sentiment_model/model_opn_sentiment_1024.bin')
    result = gol.show_opn("""after 6 hours of driving it's still not close to freezing
        being a woman it's extremely troubling and unexpected, especially as it's at the very front and runs down half way to the back of my head.
        well your rings finally arrived and what a disappointment they do not hold there shape as to being a ring or a bracelet making them impossible to wear, am so disappointed, what do you plan to do about this.""")
    print(result)

