__G__ = "(G)bd249ce4"

from socket import inet_ntoa,inet_aton
from struct import pack,unpack
from re import findall
from collections import Counter
from math import log2
from tld import get_fld,get_tld
from webbrowser import open_new_tab
from psutil import process_iter,Process,wait_procs
from os import getpid
from analyzer.logger.logger import verbose, verbose_flag, verbose_timeout

def kill_process_and_subs():
    proc = Process(getpid())
    subprocs = proc.children()
    for subproc in subprocs:
        subproc.terminate()
    stillalive = wait_procs(subprocs, timeout=2)[1]
    for p in stillalive:
        p.kill()
    proc.kill()

@verbose(True,verbose_flag,verbose_timeout,None)
def kill_python_cli():
    current = getpid()
    for p in process_iter():
        cmdline = p.cmdline()
        if " ".join(cmdline) == "python3 -m qbanalyzer.cli" and p.pid != current:
            p.kill()

@verbose(True,verbose_flag,verbose_timeout,None)
def open_in_browser(_path):
    '''
    open html file in default browser
    '''
    open_new_tab(_path)

@verbose(True,verbose_flag,verbose_timeout,None)
def get_entropy(data) -> str:
    '''
    get entropy of buffer
    '''
    try:
        if not data:
            return "0.0 (Minimum: 0.0, Max: 8.0)"
        entropy = 0
        counter = Counter(data)
        l = len(data)
        for count in counter.values():
            p_x = float(count) / l
            entropy += - p_x * log2(p_x)
        return "{} (Minimum: 0.0, Maximum: 8.0)".format(entropy)
    except:
        return "None"

@verbose(True,verbose_flag,verbose_timeout,None)
def get_entropy_float_ret(data) -> float:
    '''
    get entropy of buffer
    '''
    try:
        if not data:
            return 0.0
        entropy = 0
        counter = Counter(data)
        l = len(data)
        for count in counter.values():
            p_x = float(count) / l
            entropy += - p_x * log2(p_x)
        return entropy
    except:
        return 0.0

@verbose(True,verbose_flag,verbose_timeout,None)
def get_entropyold(data):
    probabilities = [float(data.count(char)) / len(data) for char in dict.fromkeys(list(data))]
    entropy =- sum([probability * log2(probability) / log2(2.0) for probability in probabilities])
    return entropy

@verbose(True,verbose_flag,verbose_timeout,None)
def long_to_ip(decimal) -> str:
    '''
    decimal to ip
    '''
    return inet_ntoa(pack("!L", decimal))

@verbose(True,verbose_flag,verbose_timeout,None)
def ip_to_long(ip) -> int:
    '''
    ip to decimal
    '''
    return unpack("!L", inet_aton(ip))[0]

@verbose(True,verbose_flag,verbose_timeout,None)
def get_words(data,_path) -> (list,str):
    '''
    get all words of file
    '''
    words =[]
    wordsinsensitive = []
    wordssensitive = []
    wordsstripped = ""
    encoding = data["Encoding"]["Details"]["ForceEncoding"]
    if encoding == "utf-16":
        words = findall(b"[\x20-\x7e\x00]{4,}",data["FilesDumps"][_path])
    else:
        words = findall(b"[\x20-\x7e]{4,}",data["FilesDumps"][_path])
    for x in words:
        wordssensitive.append(x.decode(encoding,errors="ignore"))
        wordsinsensitive.append(x.lower().decode(encoding,errors="ignore"))

    wordsstripped = '\n'+'\n'.join(wordsinsensitive) + '\n'
    data["StringsRAW"] = {  "wordssensitive": wordssensitive,
                            "wordsinsensitive": wordsinsensitive,
                            "wordsstripped": wordsstripped }

@verbose(True,verbose_flag,verbose_timeout,None)
def get_words_multi_files(data,arr) -> (list,str):
    '''
    get all words of multi files
    '''
    words = []
    wordsstripped = ""
    wordsinsensitive = []
    wordssensitive = []
    encoding = data["Encoding"]["Details"]["ForceEncoding"]
    for x in arr:
        if encoding == "utf-16":
            words.extend(findall(b"[\x20-\x7e\x00]{4,}",data["FilesDumps"][x["Path"]]))
        else:
            words.extend(findall(b"[\x20-\x7e]{4,}",data["FilesDumps"][x["Path"]]))
    for x in words:
        wordssensitive.append(x.decode(encoding,errors="ignore"))
        wordsinsensitive.append(x.lower().decode(encoding,errors="ignore"))
    wordsstripped = '\n'.join(wordsinsensitive)
    data["StringsRAW"] = {  "wordssensitive": wordssensitive,
                            "wordsinsensitive": wordsinsensitive,
                            "wordsstripped": wordsstripped }

@verbose(True,verbose_flag,verbose_timeout,None)
def get_words_multi_filesarray(data,arr) -> (list,str):
    '''
    get all words of buffers in an array
    '''
    words = []
    wordsstripped = ""
    wordsinsensitive = []
    wordssensitive = []
    encoding = data["Encoding"]["Details"]["ForceEncoding"]
    for x in arr:
        #if x["Path"].endswith(".xml"):
        if encoding == "utf-16":
            words.extend(findall(b"[\x20-\x7e\x00]{4,}",x))
        else:
            words.extend(findall(b"[\x20-\x7e]{4,}",x))
    for x in words:
        wordssensitive.append(x.decode('utf-8',errors="ignore"))
        wordsinsensitive.append(x.lower().decode('utf-8',errors="ignore"))
    wordsstripped = '\n'.join(wordsinsensitive)
    data["StringsRAW"] = {  "wordssensitive": wordssensitive,
                            "wordsinsensitive": wordsinsensitive,
                            "wordsstripped": wordsstripped }

def serialize_obj(obj):
    '''
    recursive str serialization obj
    '''
    try:
        if type(obj) == dict:
            for key, value in obj.items():
                obj[key] = serialize_obj(value)
        elif type(obj) == list:
            for i, item in enumerate(obj):
                obj[i] = serialize_obj(item)
        else:
            obj = str(obj)
        return obj
    except:
        pass

def check_url(url) -> bool:
    try:
        if not url.startswith(("http://","https://","ftp://")):
            url = "http://"+url
        if get_tld(url, fail_silently=True):
            root = None
            try:
                root = get_fld(url,fix_protocol=True)
            except:
                pass
            if root:
                return True
        return False
    except:
        pass