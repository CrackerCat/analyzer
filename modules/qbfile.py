__G__ = "(G)bd249ce4"


from shutil import copyfile, rmtree
from os import mkdir, path
from hashlib import md5, sha1, sha256
from magic import from_file
from ssdeep import hash_from_file
from mimetypes import guess_type
from re import match
from copy import deepcopy
from analyzer.logger.logger import verbose, verbose_flag, verbose_timeout
from analyzer.mics.funcs import get_words, get_words_multi_files, get_entropy
from analyzer.modules.archive import unpack_file

@verbose(True, verbose_flag, verbose_timeout, None)
def convert_size(s):
	for u in ['B', 'KB', 'MB', 'GB']:
		if s < 1024.0:
			return "{:.2f}{}".format(s, u)
		else:
			s /= 1024.0
	return "File is too big"

class QBFile:
	@verbose(True, verbose_flag, verbose_timeout, "Starting QBFile")
	def __init__(self):
		self.datastruct = {"Properties":{}, 
						   "_Properties":{}}

	@verbose(True, verbose_flag, verbose_timeout, None)
	def setup_malware_folder(self, folder):
		'''
		setup malware folder where files will be transferred and unpacked
		'''
		self.malwarefarm = folder
		if not self.malwarefarm.endswith(path.sep):self.malwarefarm = self.malwarefarm+path.sep
		if not path.isdir(self.malwarefarm):mkdir(self.malwarefarm)

	@verbose(True, verbose_flag, verbose_timeout, "Setting up ouput folder")
	def create_temp_folder(self, data, uuid, _path):
		'''
		create temp folder that has the md5 of the target file
		'''
		safename = "".join([c for c in path.basename(_path) if match(r'[\w\.]', c)])
		if len(safename) == 0:safename = "temp"
		md5 = data["Details"]["Properties"]["md5"]
		folder_path = self.malwarefarm+uuid+"_"+md5
		if path.exists(folder_path):
			rmtree(folder_path)
		mkdir(folder_path)
		copyfile(_path, folder_path+path.sep+"temp")
		data["Location"] = {"Original":_path, 
							"File":folder_path+path.sep+"temp", 
							"html":folder_path+path.sep+safename+".html", 
							"json":folder_path+path.sep+safename+".json", 
							"Folder":folder_path+path.sep+"temp_unpacked"}
		data["FilesDumps"] = {folder_path+path.sep+"temp":open(_path, "rb").read()}

	@verbose(True, verbose_flag, verbose_timeout, "Getting file details")
	def get_detailes(self, data, _path):
		'''
		get general details of file
		'''
		data["Details"] = deepcopy(self.datastruct)
		f = open(_path, "rb").read()
		open(_path, "rb").read(4)
		data["Details"]["Properties"]={ "Name":path.basename(_path).lower(), 
										"md5":md5(f).hexdigest(), 
										"sha1":sha1(f).hexdigest(), 
										"sha256":sha256(f).hexdigest(), 
										"ssdeep":hash_from_file(_path), 
										"size":convert_size(path.getsize(_path)), 
										"bytes":path.getsize(_path), 
										"mime":from_file(_path, mime=True), 
										"extension":guess_type(_path)[0], 
										"Entropy":get_entropy(f)}


	@verbose(True, verbose_flag, verbose_timeout, "Handling unknown format")
	def check_sig(self, data):
		'''
		start unknown files logic, this file is not detected by otehr modules
		if file is archive, then unpack and get words, wordsstripped otherwise
		get words, wordsstripped from the file only
		'''
		if  data["Details"]["Properties"]["mime"] == "application/java-archive" or \
			data["Details"]["Properties"]["mime"] == "application/zip" or \
			data["Details"]["Properties"]["mime"] == "application/zlib":
			unpack_file(data, data["Location"]["File"])
			get_words_multi_files(data, data["Packed"]["Files"])
		else:
			get_words(data, data["Location"]["File"])

	@verbose(True, verbose_flag, verbose_timeout, None)
	def analyze(self, data, uuid, _path, folder) -> bool:
		'''
		first logic to execute, this will check if malware folder exists or not
		get details of the target file and move a temp version of it to a temp
		folder that has the md5
		'''
		self.setup_malware_folder(folder)
		self.get_detailes(data, _path)
		self.create_temp_folder(data, uuid, _path)

		
