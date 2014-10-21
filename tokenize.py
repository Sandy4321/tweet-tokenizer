# coding=utf-8
import sys,re

def processClitic(token,prev):
	if prev=="I": token = re.sub(r"^ain't$","am not",token)
	elif prev=="We" or prev == "They": token = re.sub(r"^ain't$","are not",token)
	else: token = re.sub(r"^ain't$","is not",token)
	token = re.sub(r"^won't$","will not",token)
	token = re.sub(r"^can't$","can not",token)
	token = re.sub(r"n't$"," not",token)
	token = re.sub(r"'s$"," is", token)
	token = re.sub(r"s'$","s 's", token)
	token = re.sub(r"'ve$"," have",token)
	token = re.sub(r"'re$"," are",token)
	token = re.sub(r"'m$"," am",token)
	token = re.sub(r"'ll$"," will", token)
	token = re.sub(r"'d$"," would", token)
	return token

def processDateMY(token):
	match = re.search(r"(\d{1,2}\s)?([a-zA-Z]{3,9})(\s\d{4})",token)
	dictMonths = [("Jan",1),("January",1),("Feb",2),("February",2),("March",3),("April",4),("May",5),("June",6),("July",7),("August",8),("Aug",8),("September",9),("Sept",9),("October",10),("Oct",10),("November",11),("Nov",11),("December",12),("Dec",12)]
	date, month, year = "", "" , ""
	if match==None: return ("",False)
	for group in match.groups():
		if(group==None): continue
		if re.search(r"^\d{1,2}\s$",str(group)):
			date = str(group)
		elif re.search(r"^\s\d{4}$",str(group)):
			year = str(group)
		else:
			flag=False
			for m in dictMonths:
				if m[0]==str(group):
					month = str(m[1])
					if len(month)==1: month = "0"+month
					flag=True
					break
			if not flag:
				return ("",False)
	if year == "": year="????"
	year = year.strip()
	date = date.strip()
	token = "CSL772:D:"+year+"-"+month
	if date != "": token += "-"+date
	return (token,True)

def processDateDM(token):
	match = re.search(r"(\d{1,2}\s)([a-zA-Z]{3,9})(\s\d{4})?",token)
	dictMonths = [("Jan",1),("January",1),("Feb",2),("February",2),("March",3),("April",4),("May",5),("June",6),("July",7),("August",8),("Aug",8),("September",9),("Sept",9),("October",10),("Oct",10),("November",11),("Nov",11),("December",12),("Dec",12)]
	date, month, year = "", "" , ""
	if match==None:
		return ("",False)
	for group in match.groups():
		if(group==None): continue
		if re.search(r"^\d{1,2}\s$",str(group)):
			date = str(group)
		elif re.search(r"^\s\d{4}$",str(group)):
			year = str(group)
		elif re.search(r"[a-zA-Z]{3,9}",str(group)):
			flag=False
			for m in dictMonths:
				if m[0]==str(group):
					month = str(m[1])
					if len(month)==1: month = "0"+month
					flag=True
					break
			if not flag:
				return ("",False)
	if year == "": year="????"
	year = year.strip()
	date = date.strip()
	token = "CSL772:D:"+year+"-"+month
	if date != "": token += "-"+date
	return (token,True)


def processTime(token):
	match = re.search(r"(\d{1,2}(:\d{2})?)\s?(AM|PM)",token)
	meridian = ""
	time = ""
	if(match==None): return ("",False)
	for group in match.groups():
		if(group==None): continue
		if(re.search(r"^AM|PM$",str(group))):
			meridean = str(group)
		if(re.search(r"^\d{1,2}(:\d{2})?$",str(group))):
			time = str(group)
		time = re.sub(":","",time)
		if(len(time)==2): time += "00"
	if meridean=="PM":
		if(int(time)<1200): time = str(int(time)+1200)
	elif meridean=="AM":
		if(int(time)>=1200): time = str(int(time)-1200)
		while(len(time)<4):
			time = "0" + time
	elif meridian=="" and int(time) < 1200: time += "|"+ str(int(time)+1200)
	token = "CSL772:T:"+time
	return (token,True)

def processHyphen(token):
	#token = re.sub(r"^([A-Z][\w]*)\-([A-Z][\w]*)$","\\1 - \\2",token)
	#token = re.sub(r"^([0-9][\w]*)\-([0-9][\w]*)$","\\1 - \\2" ,token)
	token = re.sub(r"^([\w]*)\-([\w]*)$","\\1 -\\2",token)
	return token

def tokenize(text):
	patterns = [
			r"(mailto:)?[^\s]+@[^\s]+\.[\w]{2,6}",
			r"(https?:\/\/)?([\w\-]+\.)?[\w\-]+\.[\w]{2,6}([\/\?][\w\-\!\?\%\~\&\=\+]+[\.]?[\w\-\!\?\%\~\&\=\+]*)*\/?",
			r"(\w*)['‘`]((s)|(re)|(m)|(ve)|(d)|(ll)|(t))",
			r"[\w]+\-[\w]+",
			r"([A-Z][\s]?[\.]?[\s]){3,8}",
			r"@([A-Za-z0-9_]+)",
	  		r"#[\w\-]+",
	  		r"(\d{1,2}\s)?[a-zA-Z]{3,9}(\s\d{4})",
	  		r"\d{1,2}\s[a-zA-Z]{3,9}(\s\d{4})?",
			r"\d{1,2}(:\d{2})?\s?(AM|PM)?",
			r"(\$?([0-9]+\,)*[0-9]+(\.[0-9]+)?)|(\d+[\\\/]\d+)",
	  		r"([\<\>\}]?[\:\;B][\'\"]?[\-\^]?[\)\(\#\@\$SPpdDOoL\|\/\\]{1,3})|([\)\(\#\@\$dOo\|\/\\]{1,3}[\-\^]?[\'\"]?[\:][\<\>\{E]?)",
	  		r"[\(\)\{\}\[\]\-]",
	  		r"([\.]+)|([\!\?]+)|([\"]+)|([\']+)|([\:]+)|([\;]+)|([\,]+)",
	  		r"[a-zA-Z]+",
	  		r"[^\s\,\?\!\-\_\:\"\'\;]+",
	  		r"[^\s]",
	  		r"\s+",
		]
	tokenType=["EMAIL","URL","CLITIC","HYPHENATED","ABBREVIATION","USER_REFERENCE","HASHTAG","DATEY","DATED","TIME","NUMERAL","EMOTICON","PUNCTUATION_SEP","PUNCTUATION_COM", "WORD", "FOREIGN", "UNKNOWN"]
	
	regs = [re.compile(pattern) for pattern in patterns]
	pos = 0
	tokens=[]
	while True:
		match = False
		rnum = 0
		for reg in regs:
			match = reg.match(text, pos)
			rnum+=1
			if match:
				s = match.start()
				e = match.end()
				if(rnum==len(patterns)): break
				rnum-=1
				token=text[s:e]
				prev = ""
				if len(tokens)>0: prev=tokens[-1][1]
				if tokenType[rnum]=="CLITIC" : token = processClitic(token,prev)
				elif tokenType[rnum]=="DATEY" :
					temp = processDateMY(token)
					token = temp[0]
					temp = temp[1]
					if(temp==False): continue
				elif tokenType[rnum]=="DATED" :
					temp = processDateDM(token)
					token = temp[0]
					temp = temp[1]
					if(temp==False): continue
				elif tokenType[rnum]=="TIME" :
					temp = processTime(token)
					token = temp[0]
					temp = temp[1]
					if(temp==False): continue
				elif tokenType[rnum]=="HYPHENATED" :
					token = processHyphen(token)
				elif tokenType[rnum]=="ABBREVIATION" :
					token = re.sub("\s","",token)
				token = token.split(" ")
				token = [(tokenType[rnum],t) for t in token]
				tokens += token
				break
		if not match: break
		pos = e
	return tokens

while 1:
    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        break

    if not line:
        break
    line = line.strip();
    tokens = tokenize(line)
    print line
    print len(tokens)
    for (category,token) in tokens:
    	#print category
    	print token