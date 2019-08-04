import os
import webbrowser
import ssh

def get_ques():
	#os.system('Capture2Text_CLI.exe --screen-rect "15 264 353 515" > ocr.txt')
	#txtlb = 'Capture2Text_CLI.exe -b --screen-rect "'
	#txtl = 'Capture2Text_CLI.exe --screen-rect "'
	#txtrq = '" > ocrq.txt'
	#txtro = '" > ocro.txt'
	#coord = open('coordq.txt','r').read()
	#txtq = txtl + coord + txtrq
	#os.system(txtq)
	question = open('ocrq.txt','r',encoding='utf-8', errors='ignore').read()
	#os.system(txtlb + (open('coordo.txt','r').read()) + txtro)
	text = open('ocro.txt','r',encoding='utf-8', errors='ignore').read()
	lines = text.splitlines()
	options = []

	for line in lines:
		if line != '':
			options.append(line)
	return question , options

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
	earlywords = ['earliest','earliest?','first?','latest?']
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


def oldsearch(ques):
	prestr = 'http://www.google.co.in/search?q='
	queswords = split_string(ques)
	for w in queswords:
		prestr += (w + '+')
	webbrowser.open_new_tab(prestr)

def earliestQues(options):
	print("earliest kind of question")
	#webbrowser.open_new_tab('http://google.com')
	prestr = 'http://www.google.co.in/search?q='
	for option in options:
		reststr = ''
		words = split_string(option)
		for w in words:
			reststr += (w + '+')
		reststr +='wiki'
		webbrowser.open_new_tab(prestr+reststr)

def startssh():
	try:
		server = ssh.Connection(host='54.200.62.243', username='ubuntu', private_key='tubuntu.pem')
	except:
		print('Error Connecting to AWS Server')
		exit()
	return server

def getscores(ques, options,server):
	oldsearch(ques)
	questype = chkques(ques)
	while(True):
		x=ques.find('"')
		if x==-1:
			break
		ques = ques[:x] + ques[x+1:]
	print('ques: ' + ques)
	print(options)
	if questype==0:
		cmd = 'python3 quizbot_server.py "' + ques + '" "0" '
	elif questype==-1:
		cmd = 'python3 quizbot_server.py "' + ques + '" "-1" '
	else:
		earliestQues(options)
		return
	for option in options:
		cmd += ('"' + option + '" ')
	result = server.execute(cmd)
	result = [line.decode().strip(' \n\t') for line in result]
	print()
	for line in result:
		print(line)
	print()
	hf = open('questions_history.txt','a+', encoding = 'utf-8')
	hf.write(ques)
	hf.write(str(result))
	hf.write('\n\n')
	hf.close()
#main function
def main():

	print('QuizBot Client Version')
	server = startssh()
	while(True):
		ch = int(input('1-Capture & Search \n2 - Among these type ka question \n0 - oldStyleSearch \n-1 -Exit \n: '))
		hf = open('questions_history.txt','a+', encoding = 'utf-8')

		if ch==-1:
			break
		if ch==0:
			ques , options = get_ques()
			oldsearch(ques)
		elif ch==1 or ch==2:
			ques , options = get_ques()
			oldsearch(ques)
			#oldsearch(ques)
			if(ch==2):
				questype = 0
			else:
				questype = chkques(ques)
			while(True):
				x=ques.find('"')
				if x==-1:
					break
				ques = ques[:x] + ques[x+1:]
			print('ques: ' + ques)
			print(options)
			if(questype==0):
				if ch==1:
					cmd = 'python3 quizbot_server.py "' + ques + '" "0" '
				elif ch==2:
					cmd = 'python3 quizbot_server.py "' + ques + '" "2" '
				for option in options:
					cmd += ('"' + option + '" ')
				#server = ssh.Connection(host='54.200.62.243', username='ubuntu', private_key='tubuntu.pem')
				#print(cmd)
				result = server.execute(cmd)
				#result = [line.strip(' \n\t') for line in result]
				result = [line.decode().strip(' \n\t') for line in result]
				print()
				for line in result:
					print(line)
				print()
				inp = input()
				#findit3(ques,options)

			elif questype==-1:
				cmd = 'python3 quizbot_server.py "' + ques + '" "-1" '
				for option in options:
					cmd += ('"' + option + '" ')
				#print(cmd)
				result = server.execute(cmd)
				result = [line.decode().strip(' \n\t') for line in result]
				print()
				for line in result:
					print(line)
				print()
				inp = input()
				#findbywiki(ques,options)	
			else:
				earliestQues(options)

			
			'''
			try:
				ch = int(input())
				if(ch==1):
					oldsearch(ques)
			except:
				print('okay!')		
			'''

			
			hf.write(ques)
			for option in options:
				hf.write(option + ', ')
			hf.write('\n\n')
			hf.close()
			hf = open('questions_history.txt','a+', encoding = 'utf-8')
			#db.clear()	

if __name__ == '__main__':
	main()

