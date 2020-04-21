import os

def init(language='hebrew', monkey_by_vectors=False):
    '''
    @param: language:
        Current version has the ability to process only hebrew docs.
        In the future we'll support in more languages
    @param: monkey_by_vectors
        Load the right monkey model by the wanted method
        True: by_vectors
        False: by_sum
    '''
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    global lang_letters
    global lang_words
    global DATA_PATH
    global MODELS_PATH
    global LETTERS_MODEL
    global WORDS_MODEL
    global MONKEY_MODEL
    global LETTERS_SIZE
    global WORDS_SIZE

    DATA_PATH = 'data/'
    MODELS_PATH = 'models/'

    LETTERS_SIZE = 28
    WORDS_SIZE = 64

    lang_letters = []
    lang_words = []
    if language == 'hebrew':
        lang_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י',\
                        'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
                        'ך', 'ם', 'ן', 'ף', 'ץ']
        LETTERS_MODEL = 'hebrewLettersModel'
        lang_words = ['של', 'לא', 'את', 'גם', 'לסיכום', 'כי', 'זה',\
                        'זו', 'יש', 'לדעתי', 'אני', 'לסיכום']
        #TODO: add trained words model to Model diractory
        WORDS_MODEL = 'hebrewWordsModel'
    if monkey_by_vectors:
        MONKEY_MODEL = 'monkey_model_by_vectors.sav'
    else:
        MONKEY_MODEL = 'monkey_model_by_sum.sav'