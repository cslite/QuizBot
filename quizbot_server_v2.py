import os
#from didYouMean import didYouMean as dym 	#use this for server ubuntu 
import didYouMean as dym 	#This will not work on the server ubuntu
import sys
from google import google
import wikipedia
import urllib.request as urllib2
from bs4 import BeautifulSoup
from collections import OrderedDict
import _thread as thread


remove_words = [
    "who",
    "what",
    "where",
    "when",
    "of",
    "and",
    "that",
    "have",
    "for",
    "the",
    "why",
    "the",
    "on",
    "with",
    "as",
    "this",
    "by",
    "from",
    "they",
    "a",
    "an",
    "and",
    "my",
    "are",
    "in",
    "to",
    "these",
    "is",
    "does",
    "which",
    "his",
    "her",
    "also",
    "have",
    "it",
    "not",
    "we",
    "means",
    "you",
    "comes",
    "came",
    "come",
    "about",
    "if",
    "by",
    "from",
    "go",
    "?",
    ",",
    "!",
    "'",
    "has",
    "\""
  ]

def split_string(source):
	splitlist = ",!-.;/@ #"
	output = []
	atsplit = True
	for char in source:
		if char in splitlist:
			atsplit = True
		else:
			if atsplit:
				output.append(char)
				atsplit = False
			else:
				output[-1] = output[-1] + char
	return output

def chkques(question):
	negwords = ['not','never']
	earlywords = ['earliest','earliest?','first?']
	#thesewords = ['of these', 'among these', 'which of the following']
	queswords = split_string(question)
	#print('we r in isneg function!')
	for word in queswords:
		#print('checking - '+ word)
		lword = word.lower()
		if lword in negwords:
			#print("yeah!!")
			return -1
		if lword in earlywords:
			return 1
	return 0

#db = {}
db = OrderedDict()

# get web page (copied function)
def get_page(link):
	try:
		if link.find('mailto') != -1:
			return ''
		req = urllib2.Request(link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
		html = urllib2.urlopen(req).read()
		return html
	except (urllib2.URLError, urllib2.HTTPError, ValueError) as e:
		return ''


def findit(ques,options):
	num_page = 2
	searchres = google.search(ques,num_page)
	ques = ques.lower()

	for i in range(len(options)):
		#dymi =  dym.didYouMean(options[i].lower())
		#print(options[i] + ' - ' + '"' + str(dymi) + '"')
		#if dymi != 1 or len(dymi) > 1 or dym:
			#print('yeah')
		#	options[i] = dymi
		#else:
		options[i] = options[i].lower()
		db[options[i]] = 0

	link = searchres[0].link
	#print(link)
	content = get_page(link)
	soup = BeautifulSoup(content,"lxml")
	page = soup.get_text().lower()
	for option in options:	
		db[option] += (2 * page.count(option))

	for result in searchres:
		for option in options:
			words = split_string(option)
			lowerdesc = result.description.lower()
			for word in words:
				if len(word) < 2 or (word in ques):
					continue
				db[option] += lowerdesc.count(word)
				#if word in (lowerdesc):
					#db[option]+=1
				if (len(word)>3) and ((' '+word+' ') in lowerdesc):
					db[option] += (2*lowerdesc.count((' '+word+' ')))
					#db[option]+=2
			if (option in lowerdesc) :
				#db[option] += 2 
				db[option] += (len(words))			#update, this will give better results...
			#zero = option.find('0')				#update, no need of this now, as ocr is not needed
			#if zero!=-1:
			#	db[option] += lowerdesc.count(option[:zero]+'o'+option[zero+1:])
	for ele in db:
		print(ele + ' (' + str(db[ele]) + ') ')
	#print (db)



def cleanques(ques):
	qwords = ques.lower().split()
	cleanwords = [word for word in qwords if word not in remove_words]
	return cleanwords

def googleNOT_find(option,cleanwords,addr):
	num_page = 1
	searchres = google.search(option,num_page)
	for result in searchres:
		resdesc = (result.description).lower()
		for word in cleanwords:
			if word in (resdesc):
				db[option]+=addr

def googleNOT(ques,options,type=0):
	addr = -1
	if type==0:
		#print("This question is detected as a NOT question")
		for i in range(len(options)):
			options[i] = options[i].lower()
			db[options[i]] = 15	
	else:
		#print("These waala question")
		for i in range(len(options)):
			options[i] = options[i].lower()
			db[options[i]] = 0
		addr=1
	cleanwords = cleanques(ques)
	#print(cleanwords)
	num_page = 1
	searchres = google.search(ques,num_page)
	link = searchres[0].link
	#print(link)
	content = get_page(link)
	soup = BeautifulSoup(content,"lxml")
	page = soup.get_text().lower()
	for option in options:
		db[option] += (2*addr * page.count(option))
		searchres = google.search(option,num_page)
		googleNOT_find(option,cleanwords,addr)
		thread.start_new_thread(googleNOT_find, (option,cleanwords, addr))
		
	#print(db)
	for option in options:
		wikiresults = wikipedia.search(option)
		try:
			wikisum = wikipedia.summary(wikiresults[0],auto_suggest=True)
			#print()
			#print(wikisum)
		except:
			#print('wiki error')
			continue
		datawiki = wikisum.lower()
		for word in cleanwords:
			if word in datawiki:
				db[option] +=addr

#main function

options = []
sz = len(sys.argv)
i = 0
#for arg in sys.argv:
#	print(str(i) + '- ',end='')
#	print(arg)
#	i+=1
#print('Pay your dues to 9654711180 before 3PM, otherwise the Server will be stopped.')
ques = sys.argv[1]
qtype = int(sys.argv[2])

for i in range(3,sz):
	#we will be giving about 5 command line arguments,
	#first one will be the question, second the type and the rest are options
	options.append(sys.argv[i])
if qtype==0:
	findit(ques,options)
elif qtype==-1:
	googleNOT(ques,options)
	for ele in db:
		print(ele + ' (' + str(db[ele]) + ') ')
		#print(db[ele])
	#print(db)
elif qtype==2:
	googleNOT(ques,options,1)
	#print(db)
	for ele in db:
		#print(db[ele])
		print(ele + ' (' + str(db[ele]) + ') ')

