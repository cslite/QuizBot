from tkinter import *
#from .quizbot_server import get_ques
import os
import webbrowser
import ssh
import json
import requests
import websocket
import _thread as thread
import time

headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImRoZ2ZoamdkIiwidXNlcl91aWQiOiJUOFlKNldQTDBOIiwiaXNfc3RhZmYiOmZhbHNlfQ.jG6qIQ3-FbRLpGiEMain2RlVrHu3PD_YI8Tdjb5cnag",
           "User-Agent": "okhttp/3.8.1"}
main_url = "https://realtime.getloconow.com/socket.io/?EIO=3&transport=polling"
cookies = {}

ques = ""
options = ["","",""]

def getsid():
	global main_url
	global headers
	global cookies
	r = requests.get(main_url,headers = headers)
	rdata = r.text
	#print()
	#print(rdata)
	#print()
	try:
		cookies = r.cookies
		#print(cookies)
	except:
		print("Cookies Error!")
	try:
		rdata = rdata[rdata.find('{'):]
		rjson = json.loads(rdata)
		return rjson["sid"]
	except:
		print("There is some error in getting sid")
		return -1
qc = 1
def on_message(ws,message):
	#print('#onmessage#')
	#print(message)
	global ques
	global options
	global qc
	if message == '3probe':
		socklbl.config(text = "Connected to Socket..", fg="green")
		#print("Success!!")
	elif message != '3':
		try:
			message = message[message.find('['):]
			mdata = json.loads(message)
			if "question" in mdata:
				ques = mdata[1]["text"]
				#fq = open('ocrq.txt','w')
				#print(ques)
				#fq.write(ques)
				#fo= open('ocro.txt','w')
				#options = []
				for o in mdata[1]["options"]:
					options[o["rank"]] = (o["text"])
				#for i in range(2,-1,-1):
				#	fo.write(options[i] + '\n')
				#fo.close()
				#fq.close()
				#print("...Question Detected...(%d)" %qc)
				scanit()
				qc+=1
		except:
			print(message)

def on_error(ws,error):
	print('#onerror#')
	print(error)
def on_close(ws):
	#print('## Closed ##')
	#messagebox.showinfo("QuizBot", "WebSocket Closed")
	socklbl.config(text = "Not connected to Socket..")
def on_open(ws):
	#print('## Opened ##')
	def run(*args):
		ws.send('2probe')
		ws.send('5')
		while True:
			try:
				#print('Sending to Server...')
				time.sleep(15)
				ws.send('2')
			except:
				print('Unable to send to server')
				break
		time.sleep(1)
		ws.close()
		print ("thread terminating..")
	thread.start_new_thread(run, ())
def connectsocket(sid):
	websocket.enableTrace(True)
	global headers
	global cookies
	surl = "wss://realtime.getloconow.com/socket.io/?EIO=3&transport=websocket"
	socket_url = surl + "&sid=" + sid
	ws = websocket.WebSocketApp(socket_url,
		header= headers,
		on_message = on_message,
        on_error = on_error,
        on_close = on_close,
		cookie = 'AWSALB='+cookies['AWSALB'])
	ws.on_open = on_open
	ws.run_forever()
	sockbtn.update_idletasks()
'''
def get_ques():
	#os.system('Capture2Text_CLI.exe --screen-rect "15 264 353 515" > ocr.txt')
	txtlb = 'Capture2Text_CLI.exe -b --screen-rect "'
	txtl = 'Capture2Text_CLI.exe --screen-rect "'
	txtrq = '" > ocrq.txt'
	txtro = '" > ocro.txt'
	coord = open('coordq.txt','r').read()
	txtq = txtl + coord + txtrq
	#os.system(txtq)
	question = open('ocrq.txt','r',encoding='utf-8', errors='ignore').read()
	#os.system(txtlb + (open('coordo.txt','r').read()) + txtro)
	text = open('ocro.txt','r',encoding='utf-8', errors='ignore').read()
	lines = text.splitlines()
	options = []

	for line in lines:
		if line != '':
			options.append(line)
	if 'ELIMINATED' in question:
		question = question[10:]
	return question , options
'''
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
		reststr +='when'
		webbrowser.open_new_tab(prestr+reststr)



def scanit():
	global ques
	global options
	#ques , options = get_ques()
	queslbl.config(text = ques)
	for i in range(3):
		opt[i].config(text=options[i],fg="red") 
	questype = chkques(ques)
	while(True):
		x=ques.find('"')
		if x==-1:
			break
		ques = ques[:x] + ques[x+1:]
	cmd = 'python3 quizbot_server_gui.py "' + ques + '" "0" '
	for option in options:
		cmd += ('"' + option + '" ')
	result = server.execute(cmd)
	result = [line.decode().strip(' \n\t') for line in result]
	maxi=0
	for i in range(3):
		opt[i].config(text=(options[i]+' ('+result[i]+')'))
		result[i] = int(result[i])
		if result[i] > result[maxi]:
			maxi=i
	opt[maxi].config(fg="green") 


def sockit():
	sid = getsid()
	r2 = requests.get(main_url+"&sid="+sid, headers = headers, cookies = cookies)
	rdata2 = r2.text
	connectsocket(sid)




root = Tk()
server = ssh.Connection(host='54.200.62.243', username='ubuntu', private_key='tubuntu.pem')

headFrame = Frame(root)
headFrame.pack()


thelbl = Label(headFrame, text="QuizBot- Client Version")
conxn = Label(headFrame, text="(Connected)", fg="green")
thelbl.pack(side = LEFT)
conxn.pack(side = LEFT)
socklbl = Label(headFrame, text = "Not connected to Socket..")
socklbl.pack()

middleFrame = Frame(root)
middleFrame.pack()

sockbtn = Button(middleFrame,text="Connect to Socket...",command = sockit)
sockbtn.pack()




queslbl = Label(middleFrame,text="")
queslbl.pack()

opt = [0] * 3

opt[0] = Label(middleFrame,text="")
opt[1] = Label(middleFrame,text="")
opt[2] = Label(middleFrame,text="")
opt[0].pack()
opt[1].pack()
opt[2].pack()
root.mainloop()