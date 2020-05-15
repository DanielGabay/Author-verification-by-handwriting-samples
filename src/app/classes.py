class IdWord():
	'''
	Identified word
	'''
	def __init__(self, word_img, word_name):
		self.word_img = word_img
		self.word_name = word_name # identified word name

class IdLetter():
	'''
	Identified letter
	'''
	def __init__(self, letter_img, letter_name,letter_index):
		self.letter_img = letter_img
		self.letter_name = letter_name # identified letter name
		self.letter_index = letter_index

class Document():
	#@name: document name.
	def __init__(self, name):
		self.name = name

	'''
	at run time we'll add the following fields:
	@doc_img: save prepared document
	@id_words: list of all identified words. -> [IdWord objects]
	@id_letters: list of all identified letters.  ->[IdLetter objects]
	@monkey_features: list of features that were found at the monkey algorithem.
	@letters_ae_features -> holds the vector of auto-encoder features
	'''

class CompareDocuments():
	#@doc1 -> Document object representing the first doc
	#@doc2 -> Document object representing the second doc
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
class Stats():
	def __init__(self):
		self.tp = 0
		self.fp = 0
		self.tn = 0
		self.fn = 0
		self.ae_tp = 0
		self.ae_fp = 0
		self.ae_tn = 0
		self.ae_fn = 0
		self.monkey_tp = 0
		self.monkey_fp = 0
		self.monkey_tn = 0
		self.monkey_fn = 0
		self.conflict = 0
		self.conflict_while_same = 0
		self.conflict_while_diff = 0
		self.mark_as = ""
		self.same_author = None
		self.count_num_of_tests = 0