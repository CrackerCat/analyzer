__G__ = "(G)bd249ce4"

from re import DOTALL, MULTILINE, compile, finditer, sub
from binascii import unhexlify
from oletools.olevba3 import VBA_Parser
from olefile import OleFileIO, isOleFile
from analyzer.logger.logger import verbose, verbose_flag, verbose_timeout
from analyzer.mics.funcs import get_words_multi_filesarray, get_words

class OLEParser:
	@verbose(True, verbose_flag, verbose_timeout, "Starting OLEParser")
	def __init__(self):
		self.datastruct ={   "General":{}, 
							 "Objects":[], 
							 "Macro":[], 
							 "_General":{}, 
							 "_Objects":["Name", "Parsed"], 
							 "_Macro":["Name", "VBA"]}

	@verbose(True, verbose_flag, verbose_timeout, None)
	def get_objects(self, data, buffer) -> (list, list):
		'''
		get objects from rtf by regex
		'''
		x = compile(rb'\\objdata\b', DOTALL|MULTILINE)
		_List = []
		_Listobjects = []
		for _ in finditer(x, buffer):
			start, position = _.span()
			position += 1
			startcurlybracket = 0
			endcurlybracket = 0
			for i in range(position, position+len(buffer[position:])):
				if chr(buffer[i]) == "{":
					startcurlybracket += 1
				if chr(buffer[i]) == "}":
					endcurlybracket += 1
				if startcurlybracket == 0 and endcurlybracket == 1 or \
					endcurlybracket > startcurlybracket:
					whitespaces = sub(rb'\s+', b'', buffer[position:i])
					temp = unhexlify(whitespaces)
					tempdecoded = sub(br'[^\x20-\x7F]+', b'', temp)
					_Listobjects.append(tempdecoded)
					_List.append({"Len":len(buffer[position:i]), "Parsed":tempdecoded.decode("utf-8", errors="ignore")})
					break
		return _List, _Listobjects

	@verbose(True, verbose_flag, verbose_timeout, None)
	def get_streams(self, dump) -> (list, list):
		'''
		get streams
		'''
		_Listobjects = []
		_List = []
		ole = OleFileIO(dump)
		listdir = ole.listdir()
		for direntry in listdir:
			dirs = re.sub(r'[^\x20-\x7f]', r'', " : ".join(direntry))
			tempdecoded = sub(br'[^\x20-\x7F]+', b'', ole.openstream(direntry).getvalue())
			_Listobjects.append(tempdecoded)
			_List.append({"Name":dirs, "Parsed":tempdecoded.decode("utf-8", errors="ignore")})
		return _List, _Listobjects


	@verbose(True, verbose_flag, verbose_timeout, None)
	def get_general(self, data, f):
		'''
		Extract general info
		'''
		for k, v in OleFileIO(f).get_metadata().__dict__.items():
			if v != None:
				if type(v) == bytes:
					if len(v) > 0:
						data.update({k:v.decode("utf-8", errors="ignore")})
				else:
					data.update({k:v})

	@verbose(True, verbose_flag, verbose_timeout, None)
	def extract_macros(self, path) -> list:
		'''
		Extract macros
		'''
		List = []
		try:
			for (f, s, vbaname, vbacode) in VBA_Parser(path).extract_macros():
				List.append({"Name":vbaname, "VBA":vbacode})
		except:
			pass
		return List
	 
	@verbose(True, verbose_flag, verbose_timeout, None)
	def check_sig(self, data) -> bool:
		'''
		check if mime is ole
		'''

		if isOleFile(data["Location"]["File"]):
			return True
		else:
			return False

	@verbose(True, verbose_flag, verbose_timeout, "Analyze OLE file")
	def analyze(self, data):
		'''
		start analyzing ole logic 
		'''
		data["OLE"]=self.datastruct
		f = data["FilesDumps"][data["Location"]["File"]]
		self.get_general(data["OLE"]["General"], f)
		data["OLE"]["Objects"], objects = self.get_streams(f)
		data["OLE"]["Macro"] = self.extract_macros(data["Location"]["File"])
		#data["OLE"]["Objects"], objects = self.get_objects(data, f)
		if len(objects) > 0:
			get_words_multi_filesarray(data, objects)
		else:
			get_words(data, data["Location"]["File"])