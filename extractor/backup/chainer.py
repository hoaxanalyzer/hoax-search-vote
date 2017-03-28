#chainer.py
#Studienprojekt SumIt, Seminar fuer Computerlinguistik, Universitaet Heidelberg
#Boris Kramer Boris.Kramer@urz.uni-heidelberg.de
#Christian Simon Christian.Simon@hamburg.de
#For inline documentation execute:
#happydoc chainer.py

"""chainer.py is the module responsible for creating the lexical chains"""

class Lexchain:
	"""A python class as a complex data structure for representing the lexical chains.
	
	It has the following internal variables:
		
	self.string: The public surface structure of the lexical chain.
		
	self.extension: The lexical semantic extension of the lexical chain.
		
	self.nplist: The list noun phrases of which the lexical chain consists."""
	def __init__(self, np, sentence):
		"""The constructor initializes a lexical chain with a nounphrase and the sentence where it first occurs."""
		self.string=np.head
		self.extension=np.extension
		self.nplist=[[np,sentence]]
	def add(self,np,sentence):
		"""Adds a new noun phrase to an existing lexical chain."""
		self.nplist.append([np,sentence])
		
class Dummychain:
	"""This class is minimal lexical chain data structure only used for the initial state of arb (aktueller Referenzbereich)."""
	def __init__(self):
		self.string="dummychain"
		self.extension=[]
		self.nplist=[]

def addARB(arb,np,sentence):
	"""This function is only used for the initial state of ARB."""
	if arb.string=="dummychain":	#if arb.extension==[] and arb.nplist==[]:
		foo=Lexchain(np,sentence)	#if arb is of dummychain class make a new lexchain
		return foo
	else:
		arb.add(np,sentence)			#otherwise, simply add it
		return arb

def iterNP(text):
	"""This iterator returns the next NP in a list of sentences."""
	for sentence in range(0,len(text)):
		for np in text[sentence].nps:
			yield [np, sentence]

def backward_chainsearch(lexchainlist,nounhead):
	"""Makes a backward traversal through a list of lexical chains
	and checks, whether the nominal head (nounhead) is in the extension of a noun phrase in lexchainlist.
	Unncessary word senses are deleted. This function is especially needed for searching in the list of lexical chains (LLK)."""
	lexchainlist.reverse()
	for chain in lexchainlist:
		getsense=find_in_Extension(nounhead,chain.extension)
		if getsense>-1:						#remove unnecessary senses
			chain.extension=[chain.extension[getsense]]
			return chain
	return 0

def backward_nounsearch(nounphraselist,nounhead):
	"""Makes a backward traversal through a list of nounphrases
	and checks, whether the nominal head is in the extension of a noun phrase in nounphraselist.
	If so remove all senses to which it does not apply. This function is especially needed for searching in the list nominal heads (LOR)."""
	#print "Backward-Nounsearch"
	#print nounphraselist, nounhead
	nounphraselist.reverse()
	for np in nounphraselist:
	#	print np[0].reveal()
		getsense=find_in_Extension(nounhead,np[0].extension)
		if getsense>-1:					#remove unccessary senses
			np[0].extension=[np[0].extension[getsense]]
			return np
	return 0

def find_in_Extension(head,npextension):
	"""This function is essential for backward_nounsearch and backward_chainsearch.
	The basic question is: Can you find a nominalhead in the extension of nounphrase? 
	If so return the sense, otherwise return -1."""
	for i in range(0,len(npextension)):
		if head in npextension[i]:
			return i
	return -1

def reduceLexchains(chainlist):
	"""Removes one-element lexical chains from a list of lexical chains; needed at the very end of chaining algorithm."""
	reducelist=[]
	#firstly, figure out with lexical chains only have on element
	for item in chainlist:
		if len(item.nplist)<=1:
			reducelist.append(item)
	#secondly, remove these chains from chainlist
	for item in reducelist:
		chainlist.remove(item)
	return chainlist

def buildChains(text,depth):
	"""The implementation of our essential lexical chain building algorithm.
	For details see kettenalgorithmus.jpg"""
	nps=iterNP(text)
	#iterate through all the noun phrases of the text 
	arb=Dummychain() # the active referential space
	#llk=arb ??
	llk=[] # list of lexical chains
 	lor=[] # list of open referential spaces
	for np in nps:
		nphrase=np[0]
		sentence=np[1]
		#uncomment these lines, if you need debugging output about the current contents of ARB, LOR, LLK
		#print nphrase.head
		#print "LOR:"
		#for each in lor:
		#	print each[0].string
		#print "ARB:",arb.string
		#print "LLK:"
		#for each in llk:
		#	print each.string
		#print "-------"
		#let's do the genitive attributes first, because it's the most direct way of referencing
		if (nphrase.genattr!=0):
			#if you need to debug the genitive attribute handling, you may want to uncomment this line
			#print "Genitiv-Attribut:",nphrase.head, nphrase.genattr
			#first check, whether the genitive attribute falls into the extension of the ARB
			for each in [nphrase.genattr.head]+nphrase.genattr.nounfragments:
				if find_in_Extension(each,arb.extension)>-1:
					np[0].extend(depth)
					lor.append(np)
					arb=addARB(arb,nphrase,sentence)
					continue
			#check, whether genitive attribute determinated
			if np[0].genattrdet==1:
				for each in [nphrase.genattr.head]+nphrase.genattr.nounfragments:
					search=backward_chainsearch(llk,each)
					if search!=0:
						break
				if search!=0:
					np[0].extend(depth)
					lor.append(np)
					search.add(nphrase,sentence)
					llk.append(arb)
					arb=search
					llk.remove(search)
					continue
				#search should contain a np where the unnecessary senses are already deleted
				for each in [nphrase.genattr.head]+nphrase.genattr.nounfragments:
					search=backward_nounsearch(lor,each)
					if search!=0:
						break
				if search!=0:
					foo=Lexchain(search[0],search[1])
					foo.add(nphrase,sentence)
					lor.remove(search)
					llk.append(arb)
					arb=foo
					continue
			#if everything fails with the genitive attribute, just add it to LOR
			bar=nphrase.genattr
			bar.extend(depth)
			#print "Das wurde hinzugefuegt:",bar.reveal()
			lor.append([bar,sentence])
			continue
		#if the thing with the genitive attribute doesn't work out, try it the usual way with finding the head in ARB
		#if the head of the np did not suffice, try all the proper noun fragments
		#for example: if "Pope John Paul II" not in arb.extension, try pope, john, paul, ii
		for each in [nphrase.head]+nphrase.nounfragments:
			if find_in_Extension(each,arb.extension)>-1:
				np[0].extend(depth)
				lor.append(np)
				arb=addARB(arb,nphrase,sentence)
				continue
		if np[0].determinated==1:
			#Search LLK
			for each in [nphrase.head]+nphrase.nounfragments:
				search=backward_chainsearch(llk,each)
				if search!=0:
					break
			if search!=0:
				np[0].extend(depth)
				lor.append(np)
				search.add(nphrase,sentence)
				llk.append(arb)
				arb=search
				llk.remove(search)
				continue
			#Search LOR
			for each in [nphrase.head]+nphrase.nounfragments:
				search=backward_nounsearch(lor,each)
				if search!=0:
					break
			if search!=0:
				foo=Lexchain(search[0],search[1])
				foo.add(nphrase,sentence)
				lor.remove(search)
				llk.append(arb)
				arb=foo
			else:#if everyhing fails despite determination, just add np to lor
				np[0].extend(depth)
				lor.append(np)
				continue
		else:
			nphrase.extend(depth)
			foo=Lexchain(nphrase,sentence)
			llk.append(foo) 
	#append ARB to LLK
	llk.append(arb)
	#remove 1-element chains from LLK
	llk=reduceLexchains(llk)
	return llk

def printLexchains(chain):
	"""Prints a lexical chain with its name and every np assigned on standard out.""" 
	for item in chain:
		print "Lexical chain:", item.string
		for i in item.nplist:
			try:
				print i[0].string, i[1]
			except:
				print i
		print "--------------------"

def generateLexChainsHTML(chain):
	"""Generates an HTML output of a lexical chain for the CGI interface. 
		Pretty much the same as printlexchains with HTML"""
	for item in chain:
		print "Lexical chain:", item.string,"<BR>"
		for i in item.nplist:
			try:
				print i[0].string, i[1],"<BR>"
			except:
				print i,"<BR>"
		print "--------------------<BR>"

def getChains(text,depth):
	"""This is the public function required by sumit.py.
	It takes a tokenized text and the desired extensional depth when searching wordnet and return a list of lexical chains.""" 
	chains=buildChains(text,depth)
	return chains
