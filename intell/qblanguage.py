__G__ = "(G)bd249ce4"

from nltk.corpus import words
from nltk import word_tokenize
from nltk.corpus import wordnet
from string import punctuation
from copy import deepcopy
from analyzer.logger.logger import verbose, verbose_flag, verbose_timeout

@verbose(True, verbose_flag, verbose_timeout, "Checking misspelled words")
def check_spelling(data, sentence) -> dict:
	correct = []
	wrong = []
	removedpunc = (sentence.translate(str.maketrans('', '', punctuation))).lower()
	for word in word_tokenize(removedpunc):
		#if in wordnet.synsets or words.words then correct
		if not wordnet.synsets(word.rstrip()):
			if word.rstrip() not in set(words.words()):
				if word not in wrong:
					wrong.append(word)
				continue
		if word not in correct:
			correct.append(word)
	for x in set(correct):
		data["Spelling"].append({"Count":correct.count(x), "Word":x, "Misspelled":"No"})
	for x in set(wrong):
		data["Spelling"].append({"Count":wrong.count(x), "Word":x, "Misspelled":"Yes"})
	if len(correct)>0:
		data["Spelling count"].append({"Total":len(correct), "Misspelled":"No"})
	if len(wrong)>0:
		data["Spelling count"].append({"Total":len(wrong), "Misspelled":"Yes"})

class QBLanguage:
	@verbose(True, verbose_flag, verbose_timeout, "Starting QBLanguage")
	def __init__(self):
		self.datastruct = {  "English":[], 
							 "UnKnown":[], 
							 "Partly English":[], 
							 "Spelling count":[], 
							 "Spelling":[], 
							 "_English":["Count", "Word"], 
							 "_UnKnown":["Count", "Word"], 
							 "_Partly English":["Count", "Word"], 
							 "_Spelling count":["Total", "Misspelled"], 
							 "_Spelling":["Count", "Word", "Misspelled"]}

	@verbose(True, verbose_flag, verbose_timeout, "Finding english strings")
	def check_with_english(self, _data):
		'''
		check if words are english words or not
		'''
		_dict = {"UnKnown":[], "English":[], "Partly English":[], "Suspicious":[]}
		if len(self.words) > 0:
			for _word in set(self.words).intersection(set(words.words())):
				_data["English"].append({"Count":"Unavailable", "Word":_word})
			for _word in (set(self.words) - (set(words.words()))):
				_data["UnKnown"].append({"Count":"Unavailable", "Word":_word})

	@verbose(True, verbose_flag, verbose_timeout, None)
	def sort_by_len(self, _dict):
		return sorted(_dict, key=lambda l:(len(str(l))))

	@verbose(True, verbose_flag, verbose_timeout, None)
	def analyze(self, data, parsed):
		'''
		start pattern analysis for words and wordsstripped
		'''
		data["Language"] = deepcopy(self.datastruct)
		self.words = data["StringsRAW"]["wordsinsensitive"]
		self.wordsstripped = data["StringsRAW"]["wordsstripped"]
		self.check_with_english(data["Language"])
		if parsed.spelling:
			check_spelling(data["Language"], data["StringsRAW"]["wordsstripped"])