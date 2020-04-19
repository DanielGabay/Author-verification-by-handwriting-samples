class IdWord():
	def __init__(self, word_img, word_name):
		self.word_img = word_img
		self.word_name = word_name

class IdLetter():
	def __init__(self, letter_img, letter_name):
		self.letter_img = letter_img
		self.letter_name = letter_name

class Document():
	'''
	@name: document name.
	@doc_img: save prepared document
	@id_words: list of all identified words. -> [IdWord objects]
	@id_letters: list of all identified letters.  ->[IdLetter objects]
	@monkey_features: list of features that were found at the monkey algorithem.
	'''
	def __init__(self, name, id_words=None, doc_img=None, id_letters=None, monkey_features=None):
		self.name = name
		self.doc_img = doc_img
		self.id_words = id_words
		self.id_letters = id_letters
		self.monkey_features = monkey_features

class CompareDocuments():
	def __init__(self, doc1, doc2):
		self.doc1 = doc1
		self.doc2 = doc2

	'''
	at run time we'll add the following fields:
	self.monkey_results -> dict: {<result>: <value1>, <precent>: <value2>}/
								*	value1: String -> 'Same'/'Different'
						  		* 	value2: algo result, number between (0-1)
	self.letters_ae_results -> dict: same as above
	self.words_ae_results -> dict: same as above
	self.final_result -> dict: same as above, after summarize all algos results
	'''