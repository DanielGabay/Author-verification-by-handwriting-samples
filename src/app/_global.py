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
    global ae_letters
    global DATA_PATH
    global MODELS_PATH
    global LETTERS_MODEL
    global WORDS_MODEL
    global MONKEY_MODEL
    global LETTERS_SIZE
    global WORDS_SIZE
    global AE_LETTERS_MODEL
    global ae_trained_letters
    global OBJ_PATH

    DATA_PATH = 'data/'
    MODELS_PATH = 'models/'
    OBJ_PATH = 'objects/'

    LETTERS_SIZE = 28
    WORDS_SIZE = 64

    lang_letters = []
    lang_words = []
    ae_trained_letters = []
    if language == 'hebrew':
        lang_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י',\
                        'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
                        'ך', 'ם', 'ן', 'ף', 'ץ']
        LETTERS_MODEL = 'hebrewLettersModel'
        lang_words = ['של', 'לא', 'את', 'גם', 'לסיכום', 'כי', 'זה',\
                        'זו', 'יש', 'לדעתי', 'אני', 'לסיכום']
        # ae_trained_letters = ['א' ,'פ','ל','ב','ס' ,'ם','מ' ,'ח','ד' ,'ה']
        ae_trained_letters = ['ה', 'ד','ח','מ','ם','ב','ל','פ']
        # ae_trained_letters = ['א' ,'פ','ל','ב','מ' ,'ח','ד' ,'ה']
        #TODO: add trained words model to Model diractory
        WORDS_MODEL = 'hebrewWordsModel'
        AE_LETTERS_MODEL = 'ae_diff_vectors_letters.sav'
    if monkey_by_vectors:
        MONKEY_MODEL = 'monkey_model_by_vectors.sav'
    else:
        MONKEY_MODEL = 'monkey_model_by_sum.sav'