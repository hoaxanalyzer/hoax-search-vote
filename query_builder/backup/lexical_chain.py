# Natural Language Toolkit: Lexical Chaining Algorithms
#    According to:
#        Galley/McKeown 2003: Improving Word Sense Disambiguation in Lexical Chaining
#        Silber/McKoy 2000: Efficiently Computed Lexical Chains As an Intermediate Representation for Automatic Text Summarization
#
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Tassilo Barth <tbarth@coli.uni-saarland.de>
# Thanks to: Malcolm Augat and Margaret Ladlow, whose Galley/McKeown implementation served as inspiration.
# 
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

from collections import defaultdict 
from nltk.corpus import wordnet as wn
import logging

logging.basicConfig()
log = logging.getLogger("lexchain")
log.setLevel(logging.WARNING)


""" To discuss:

    - Check: 
        Should we have chains that don't have an "owner" node. I.e. cEfficiently Computed Lexical Chains As an Intermediate Representation for Automatic Text Summarizationhain for sense A, but no node with sense A in there (they might all have been deleted)
        Currently: Chains for which the owner is not at first pos are discarded
    - What to do with composite terms, e.g. tired programmer vs. programmer, where the two nodes are solely linked through programmer (i.e. tired programmer as such is not in WordNet)
        Should the tired programmer and programmer be forced to use the same sense of programmer? Currently, that's not the case.
"""


class Node(object):
    """ Base class for nodes in the LexGraph. """
    def __init__(self):
        self.adjacentNodes = {}
    def linkTo(self, target, link):
        """ Creates a undirected edge between this node and some other node.
        
        @param target: the other node
        @param link: LinkData instance containing arbitrary data related to the edge 
        """
        self._typeCheckNode(target)
        self._typeCheckLink(link)
        "What happens when already linked to target? -> ignore, relink"
        self._addToEdge(target, link)
        target._addToEdge(self, link)
        
    def _removeFromEdge(self, target):
        """ Remove this node's side from an edge shared with target """
        del self.adjacentNodes[target]
        
    def _addToEdge(self, target, link):
        """ Add this node's side to an edge shared with target """
        self.adjacentNodes[target] = link
        
    def unlink(self, target):
        """ Removes edge between this node and target node.
        
        @param: other Node
        """
        self._typeCheckNode(target)
        target._removeFromEdge(self)
        self._removeFromEdge(target)
    def unlinkAll(self):
        """ Removes all edges of this node. """
        nodesToUnlink = list(self.getAdjacentNodes())
        for target, _ in nodesToUnlink:
            self.unlink(target)
        assert len(self.adjacentNodes) == 0
    def isLinkedTo(self, target):
        """ @return: True if this node shares an edge with target """
        self._typeCheckNode(target)
        return target in self.adjacentNodes
    def getAdjacentNodes(self):
        """ 
        @return: an iterator over the nodes linked to this one. Elements of the iterable are (Node, LinkData) tuples.
        """
        return self.adjacentNodes.iteritems()
    def getId(self):
        """ @return: int, unique ID of this node. """
        raise NotImplementedError("Please implement in subclass")
    
    def _typeCheckNode(self, obj):
        if not isinstance(obj, Node): raise TypeError 
    def _typeCheckLink(self, obj):
        if not isinstance(obj, LinkData): raise TypeError

class MetaChain(Node):
    """ A type of node representing word senses (roughly).
    
    Is linked to a set of LexNode instances which are lexically related to the sense represented by the MetaChain.
    The nodes are ordered by the time of their insertion into the chain.  
    """ 
    def __init__(self, id):
        """
        firstNode = LexNode defining the sense this chain represents
        firstLink = Link data """
        Node.__init__(self)  
        self.id = id
        self.nodeOrder = []
    def getId(self):
        """ Returns ID which is the sense of this chain """
        return self.id

    def getLexNodes(self):
        """ Alias for getAdjacentNodes() """
        return self.getAdjacentNodes()
    
    def _removeFromEdge(self, target):
        Node._removeFromEdge(self, target)
        "O(len(nodeOrder))"
        self.nodeOrder.remove(target)
        
    def _addToEdge(self, target, link):
        Node._addToEdge(self, target, link)
        self.nodeOrder.append(target)
    
    def asList(self):
        """ Returns list view on items """
        return list(self.getAdjacentNodes())
    
    def getAdjacentNodes(self):
        """ 
        @return: an iterator over a list containing the LexNodes in this MetaChain. Elements of the list are (LexNode, LinkData) tuples.
        """
        for n in self.nodeOrder:
            yield n, self.adjacentNodes[n]
            
    def _typeCheckNode(self, obj):
        if not isinstance(obj, LexNode): raise TypeError
    
    """ Some definitions to use MetaChain like a tuple """
    def __len__(self):
        return len(self.adjacentNodes)
    def __getitem__(self, k):
        return self.adjacentNodes[k]
    def __iter__(self):
        return self.getAdjacentNodes()
    def __hash__(self):
        return self.getId().__hash__()
    def __eq__(self, other):
        return (False if not isinstance(other, MetaChain) else self.getId() == other.getId())
    def __str__(self):
        return str(self.getId())+":"+str([node for node in self.nodeOrder])+")"
    def __repr__(self):
        return self.__str__()
    
class LexNode(Node):
    
    """ Representation of a word token, its position in the document and its (supposed) sense.
    
    Will be linked to MetaChains.
    """
    def __init__(self, wordIndex, word, sensenum, spos=0, ppos=0):
        """
        @param wordIndex: position of the word in the document
        @param word: the word string
        @param sensenum: some sense id
        @param spos: number of the sentence this token is in
        @param ppos: number of the paragraph this token is in
        """
        Node.__init__(self)
        
        self.word = word
        self.sensenum = sensenum
        self.wordIndex = wordIndex
        
        self.spos = spos
        self.ppos = ppos
    
    def _typeCheckNode(self, obj):
        if not isinstance(obj, MetaChain): raise TypeError
    
    
    def __str__(self):
        return '%s_%s_%d'%(self.word, self.sensenum, self.wordIndex)
    def __repr__(self):
        return self.__str__()
    def __hash__(self):
        return (self.sensenum, self.word, self.wordIndex).__hash__()
    def __eq__(self, other):
        if not isinstance(other, LexNode):  return False
        return other.sensenum == self.sensenum and other.wordIndex == self.wordIndex and other.word == self.word 
    def getWord(self):
        """ @return: word string """
        return self.word
    def getSense(self):
        """ @return: sense ID, int """
        return self.sensenum
    def getId(self):
        """ @return: sense ID, int """
        return self.sensenum if self.sensenum else self.word
    def getWordIndex(self):
        """ @return: Word index, int """
        return self.wordIndex
    def copy(self):
        """ Makes a copy of this node and all of its chain memberships. 
        Will insert the copy into each chain this node is a member of.
        
        @return: The new LexNode instance """
        lnNew = LexNode(self.wordIndex, self.word, self.sensenum, self.spos, self.ppos)
        for target, link in self.getAdjacentNodes():
            lnNew.linkTo(target, link)
        return lnNew
    def getMetaChains(self):
        """ Alias for getAdjacentNodes() """
        return self.getAdjacentNodes()
    
    def getPos(self):
        """ @return: Tuple of sentence and paragraph number of this node """
        return self.spos, self.ppos
    def getDist(self, other):
        """
        @param other: LexNode to which the distance is computed  
        @return: Tuple of distances between sentence and paragraph positions of this and another node. """
        return abs(self.spos - other.spos), abs(self.ppos - other.spos)

class LinkData:
    
    class Type:
        """ Simple enum-like class """
        count = 7
        IDENT, SYN, HYPER, HYPO, SIBLING, TERM, OTHER  = xrange(count)
        @classmethod
        def validate(cls, val):  
            if not 0 <= val <= cls.count:   raise TypeError(str(val)+" is not a valid LinkData.Type")
            
    """  Container object storing information about a link (edge) between two Nodes
        (i.e. LexNode and MetaChain)
    """
    def __init__(self, lexDist=0, type=Type.OTHER):
        '''
        @param lexDist: the lexical distance between the nodes (usually WordNet tree distance)
        @param type: Type of the relation
        '''
        LinkData.Type.validate(type)
        
        self.lexDist = lexDist
        self.type = type
        
    def getLexDist(self):
        """
        @return: the lexical distance between the nodes
        """
        return self.lexDist
    
    def getType(self):
        """
        @return: Type of the relation
        """
        return self.type
    
class LexGraph(object):
    """
    Abstract base class for lexical chaining algorithms. 
    Comprises a collection of intermediate chain representations (MetaChains) and methods to iterate over / expand word tokens.
    Handles the creation of a "lexical graph", a set of interconnected lexical items.
    It is up to the subclasses to implement the scoring and final chaining components.
    
    LexGraph is always in one of three states: 
        empty: no nodes in the graph
        non-reduced: all possible meta chains for a document are created
        reduced: only one sense node per word occurrence, redundant edges deleted, actual lexical chains remain 
    
    Basic flow between these states:
        empty:    x = LexGraph(), x.reset()
        non-reduced:    x.feedDocument(paragraphs)
        reduced:    chains = x.computeChains()
        
    The base class already implements the first two states. Subclasses have to implement the reduce operation.
    """
    
    class InputError(ValueError):
        pass
    
    def __init__(self, data=None, additionalTerms={}, wnMaxdist=3):
        """ 
        @param data: Document data to be analyzed. List of paragraphs. See L{feedDocument} and especially L{feedSentence}
                     for more information about the input format.
        @param additionalTerms: A dict containing external term relationships. Format:
                                term1 -> [term2, term3, ... termN]
                                Where term1 and term2..N are assumed to be connected by a LinkData.Type.TERM relation.
        @param wnMaxdist: Maximum search distance (in edges starting from a given synset) in the WN hypernym graph.
        
        """
          
        self.reset()
        
        self.maxdist = wnMaxdist
    
        self.additionalTerms = additionalTerms
        
        if data:
            self.feedDocument(data)
    
    def reset(self):
        """ (Re-)Initializes all instance vars. """
        
        """ @ivar chains: Dict mapping MetaChain IDs onto MetaChain instances """ 
        self.chains = {}
        """ @ivar words: Dict mapping word strings onto sets of LexNode instances -- there should be one LexNode for each word instance and possible sense"""
        self.words = defaultdict(set)
        self.wordInstances = []
        """ @ivar sentpos: Sentence number """
        """ @ivar parapos: Paragraph number """ 
        self.sentpos = self.parapos = self.wordpos = 0
        
        self.reduced = False
    
    def feedDocument(self, paragraphs, reset=True):
        """ Resets the LexGraph (if reset = True, default) and builds lexical graph for a whole document.
        @param paragraphs: List of paragraphs. Each paragraph will be fed into L{feedParagraph}.
        @param reset:    Reset LexGraph?
        """ 
        self.reset()
        for para in paragraphs:
            self.feedParagraph(para)
    
    def feedParagraph(self, sentences):
        """ Builds lexical graph for a paragraph.
        @param paragraphs: List of sentences. Each sentence will be fed into L{feedSentence}.
        """ 
        self.parapos += 1
        for sent in sentences:
            self.feedSentence(sent)
            
    def feedSentence(self, chunks):
        """ Builds lexical graph for a sentence.
        @type chunks: list 
        @param chunks: Elements of this list can follow two formats:
         
            1. Tagged tokens, i.e. tuples: (token, POS tag)
               In that case, a very simple shallow chunk heuristic will group APs and NPs
               and insert them into the lexical chains. Elements not recognized to belong to 
               one of these two phrase types are dropped.
               Example input: [("lexical", "JJ"), ("chain", "NN")]
            2. Lists of tokens: [token1, token2, ...] and single tokens.
               Example input: [["lexical", "chain"], "algorithm"]
               where each list is treated as a chunk (see below) and each word
               as a single noun token.
               All elements are directly inserted into the lexical chains.
               
            In either case, the rightmost noun is treated as the semantic headword. If the 
            chunk in its entirety can not be related to another term, the procedure will try 
            to find relations only for the headword. Note that still the whole chunk will be 
            added to the lexical chains, but the chain membership is based solely on the headword.
        """ 
        self.sentpos += 1
        if not chunks: return
        if isinstance(chunks[0], tuple):
            chunks = self._handleTaggedInput(chunks)
        for chunk in chunks:
            self._addWord(chunk)
            
    def computeChains(self):
        """ Reduce LexGraph and return final lexical chains.
        
        @return: A list of tuples: (chain, chain score), where chain is a MetaChain instance and score is a float  
        """
        "This should remove all superfluous nodes"
        if not self.isReduced():
            self._reduceGraph()
        
        "Now the LexGraph is reduced and we can score the chains."
        scoredChains = []
        for ch in self.chains.itervalues():
            score = self._scoreChain(ch)
            if score > 0:
                scoredChains.append((ch, score))
                
        return scoredChains
    
    def isReduced(self):
        """  
        @return: True if word occurrences have been disambiguated and the original meta chains 
                    are resolved to the actual lexical chains.
        """ 
        return self.reduced
    
    @classmethod
    def chainsAsList(cls, scoredChains):
        """ View a list of scored chains (return value of computeChains) as a list of plain python lists of lex nodes
        """
        return [[ln for ln, _ in ch.getAdjacentNodes()] for ch, _ in scoredChains]
    @classmethod
    def chainsAsRankedList(cls, scoredChains):
        """ View a list of scored chains (return value of computeChains) as a list of plain python lists of lex nodes, sorted by their score, from highest to lowest.
        """
        return cls.chainsAsList(cls.chainsAsRanked(scoredChains))
    @classmethod
    def chainsAsRanked(cls, scoredChains):
        """ Sort a list of scored chains (return value of computeChains) by their score, from highest to lowest.
        """
        return sorted(scoredChains, key=lambda (k,v): v, reverse=True)
    
    def _handleTaggedInput(self, taggedWords):
        """ Primitive chunker, based on POS tags.
            Chunk format: Adj N+
        """
        chunk = []
        lastPostag = None
        for wordpostag in taggedWords:
            try:
                word, postag = wordpostag
            except ValueError:
                raise LexGraph.InputError("POS-tagged input assumed - has to be of format [(token, POS), .... ]!" +
                                          " Current element was: %s"%(str(wordpostag)))
            if len(postag) == 0:
                raise LexGraph.InputError("Empty POS tag in input: %s"%(str(wordpostag)))
            "We look for combinations of adjectives and nouns"
            if postag[0] == 'N':
                chunk.append(word)
            elif postag == 'JJ' and len(chunk) == 0:
                chunk.append(word)
            elif len(chunk) > 0 and lastPostag[0] == "N":
                yield chunk
                chunk = []
            lastPostag = postag
        if chunk:
            yield chunk
        
    
    def _makeLink(self, ln, type, chain=None, lexDist=0):
        """
        Factory method to be overridden by subclasses wishing to implement specific linking behaviour
        (such as additional scoring)
        """
        return LinkData(lexDist, type)
    
    def _addToChain(self, ln, senseOrToken=None, lexDist=0, type=LinkData.Type.IDENT):
        """ Add LexNode to chain identified by sense number or a word string.
        
        @param ln:    LexNode
        @param senseOrToken:    Either a sense number (int) or a word string. If None (default), take sense number from ln.
        @param lexDist:    Lexical distance between senseOrToken and ln (e.g. some kind of WordNet distance). May be used for scoring by some LexChaining algorithms. Should be 0, if sense == ln.sense
        @param type:    Type of the relation between ln and senseOrToken (One of LinkData.Type)
        
        @invariant: All senses of the word seen before the current one are represented as their own MetaChain, i.e. each word 'owns' a MetaChain
        @postcondition: If there is a lexical relationship between two words, the word positioned further in the text is linked to the MetaChain of the first word
        """ 
        senseOrToken = ln.getId() if not senseOrToken else senseOrToken
        try:
            chain = self.chains[senseOrToken]
            link = self._makeLink(ln, type, chain, lexDist)
            chain.linkTo(ln, link)
            log.debug("added "+str(ln)+" to chain "+str(chain))
        except KeyError:
            "A new chain always has to start with a node owning the chain (i.e. lexnode ID = chain ID)"
            "TODO discuss how this might affect coverage"
            if lexDist == 0:
                link = self._makeLink(ln, type, None, lexDist)
                self.chains[senseOrToken] = chain = MetaChain(senseOrToken)
                chain.linkTo(ln, link)
                log.debug("created new chain for "+str(ln))
        
            
    def _addWord(self, word):
        """ Add token to LexGraph.
        
        @param word: Either a string or a list of strings (i.e. a multi-word chunk)  
        """
        
        self.wordpos += 1
        
        log.debug("Adding "+str(word)+" at "+str(self.wordpos))
        wordSet = set()
        self.wordInstances.append(wordSet)
        
        "_expandWord assumption: senses / terms of the word as such are discovered first and returned with dist 0"
        for wnSense, term, dist, type in self._expandWord(word):
            if not wnSense:
                #id = self._idForUnknownLemma(term)
                if dist == 0:
                    ln = LexNode(self.wordpos, term, None, self.sentpos, self.parapos)
                    self._addToChain(ln)
                    wordSet.add(ln)
                else:
                    if term in self.chains:
                        assert ln
                        self._addToChain(ln, term, dist, type)
                        log.info("Term connection between "+str(word)+" and "+str(term))
            else:
                if dist == 0:
                    "Another word sense: Create own LexNode"
                    ln = LexNode(self.wordpos, term, wnSense, self.sentpos, self.parapos)
                    wordSet.add(ln)
                    self._addToChain(ln)
                else:
                    assert ln
                    self._addToChain(ln, wnSense, dist, type)
        
        wordKey = list(wordSet)[0].getWord()
        self.words[wordKey].update(wordSet)
                    
                    
    def _expandWord(self, word, maxDist=None, inclOtherRels=False):
        """ Generator which returns all senses / terms linked to word
        
        @param word: Either a string or a list of strings (i.e. a multi-word chunk)
        @param maxDist: maximum distance between found sense and word. Default None, in which case self.maxdist is used
        @param inclOtherRels: Include additional WN relations such as meronyms, also_see etc. Default False 
        @return: Tuple (sense number, lemma, lexical distance, type of relation) 
        """
        maxDist = maxDist if maxDist else self.maxdist
        if isinstance(word, list):
            headWord = word[-1]
            word = " ".join(word)
        else:
            headWord = word
        
        def expandLst(lst, alreadySeen, word, dist, type):
            for synset in lst:
                if synset.offset not in alreadySeen:
                    alreadySeen.add(synset.offset)
                    "Is this a smart thing to do? There are multiple lemmas associated with a synset and we should return a sensible lemma"
                    "So we just pick the first one"
                    firstLemmaInSynset = synset.lemmas[0]
                    yield synset.offset, firstLemmaInSynset.name.replace("_"," "), dist, type
        syns = wn.synsets(word.replace(" ","_"), "n") 
        if not syns and word not in self.additionalTerms:
            syns = wn.synsets(headWord, "n")
        if not syns:
            yield None, word, 0, LinkData.Type.IDENT
            relTerms = self.additionalTerms.get(word, None) or self.additionalTerms.get(headWord, None)
            if relTerms:
                for term in relTerms:
                    if term != word:
                        yield None, term, 1, LinkData.Type.TERM
        else:
            for syn in syns:
                yield syn.offset, word, 0, LinkData.Type.SYN
                alreadySeen = set()
                alreadySeen.add(syn.offset)
                
                hyperBases = [syn]
                hypoBases = [syn]
                for dist in range(1, maxDist):
                    newHypers = sum([h.hypernyms() for h in hyperBases], [])
                    newHypos = sum([h.hyponyms() for h in hypoBases], [])
                    for el in expandLst(newHypers, alreadySeen, word, dist, LinkData.Type.HYPER):
                        yield el
                    for el in expandLst(newHypos, alreadySeen, word, dist, LinkData.Type.HYPO):
                        yield el
                    "Do not consider uncles etc"
                    if dist == 1:
                        for el in expandLst(sum([h.hyponyms() for h in newHypers], []), alreadySeen, word, dist, LinkData.Type.SIBLING):
                            yield el                    
                    hyperBases, hypoBases = newHypers, newHypos
                
                if inclOtherRels:
                    otherRels = [syn.instance_hypernyms, syn.instance_hyponyms, syn.also_sees, syn.member_meronyms, syn.part_meronyms, syn.substance_meronyms, syn.similar_tos, syn.attributes, syn.member_holonyms, syn.part_holonyms, syn.substance_holonyms]
                    for rel in otherRels:
                        for el in expandLst(rel(), alreadySeen, word, 1, LinkData.Type.OTHER):
                            yield el
    
    def _getRelBetweenNodes(self, ln1, ln2):
        """ Assuming that both, ln1 and ln2, have been processed and added to their respective MetaChain,
        this method will determine the reason (i.e. relation type) why ln2 has been added to ln1. This is the relation between the two nodes.
        If ln2 is not in ln1's MetaChain, there is no relation. 
        
        @param ln1: LexNode
        @param ln2: LexNode
        """  
        if ln1.getWord() == ln2.getWord():    return LinkData.Type.IDENT
        if ln1.getSense() == ln2.getSense():    return LinkData.Type.SYN
        assert ln1.getId() in self.chains and ln2.getId() in self.chains
        ln1Chain = self.chains[ln1.getId()]
        ln2Chain = self.chains[ln2.getId()]
        "We might need to try both, depending on which LN has been processed first"
        try:    return ln1Chain[ln2].getType()
        except KeyError:
            try:    return ln2Chain[ln1].getType()
            except KeyError:    return None
    
    def _scoreLnk(self, ln, lnk, lnOther, lnkOther):
        raise NotImplementedError("To be implemented by subclasses")
    
    def _scoreChain(self, chain):
        "Linear sum of all links in the chain"
        if len(chain) <= 1: return 0
        score = 1.0
        owningNodeExists = False
        chainLst = chain.asList()
        if chainLst[0][0].getId() != chain.getId():   return 0
        for ind in xrange(len(chainLst)-1):
            ln, lnk = chainLst[ind]
            owningNodeExists = owningNodeExists or ln.getId() == chain.getId()
            lnOther, lnkOther = chainLst[ind+1]
            score += self._scoreLnk(ln, lnk, lnOther, lnkOther)
        if not owningNodeExists:
            return 0
        return score
    
    def _reduceGraph(self):
        raise NotImplementedError("To be implemented by subclasses")

    
""" Actual implementations of LexGraph: """


class GalleyMcKeownChainer(LexGraph):
    """ A linear time lexical chain algorithm as described by Galley and McKeown.
    Follows a one sense per discourse assumption, i. e., each word in the document
    is assumed to have only one sense that applies to all occurrences of the word.
    
    This implementation is inspired by:
    @author: Malcolm Augat <maugat1@cs.swarthmore.edu>,
    @author: Meggie Ladlow <margarel@cs.swarthmore.edu> 
    """
    
    def __init__(self, data=None, additionalTerms={}, wnMaxdist=3):
        LexGraph.__init__(self, data=data, additionalTerms=additionalTerms, wnMaxdist=wnMaxdist)
    
    def _disambiguate(self):
        """
        Returns a dictionary mapping all words in the LexGraph to their best
        WordNet senses.
        Deletes redundant links.
        """
        wsdict = {}
        for word in self.words:
            dis = self._disambiguateWord(word)
            wsdict[word] = dis
        "Now remove all other LNs from all their lexical chains"
        for word, lns in self.words.iteritems():
            for ln in lns:
                if wsdict[word].getSense() != ln.getSense():
                    log.debug("Unlink "+str(ln))
                    ln.unlinkAll()
            self.words[word] = set([wsdict[word]])
    
    def _disambiguateWord(self, word):
        """
        Disambiguates a single word by returning the sense with the highest
        total weights on its edges.

        @param word: the word to _disambiguate (string)
        """
        maxscore = -1
        maxsense = None
        log.debug("Disambiguating "+str(word)+". Has senses: "+str(self.words[word]))
        for ln in self.words[word]:
            score = self._scoreNode(ln)
            if score > maxscore:
                maxscore, maxsense = score, ln
        log.debug("    Chosen: "+str(maxsense))
        return maxsense
                
    def _scoreNode(self, ln):
        """ Computes the score of a single LexNode

        @param ln: LexNode
        """
        score = 0
        "For each meta chain this node is in:"
        for chain, lnk in ln.getMetaChains():
            "For each LN in that chain"
            for otherLn, otherLnk in chain.getLexNodes():
                "Do not score nodes belonging to the same word token!"
                if otherLn.getWordIndex() == ln.getWordIndex():    continue
                score += self._scoreLnk(ln, lnk, otherLn, otherLnk)
        return score
    
    def _scoreLnk(self, ln, lnk, lnOther, lnkOther):
        sdist, pdist = ln.getDist(lnOther)
        return self._getScoreFromMatrix(self._getRelBetweenNodes(ln, lnOther), sdist, pdist)
        
    def _getScoreFromMatrix(self, rel, sd, pd):
        '''  Implementation of scoring matrix given by Galley & McKeown 2003
        @param rel: relation type
        @param sd: sentence dist
        @param pd: paragraph dist 
        @return: float, score
        '''
        if rel == LinkData.Type.IDENT or rel == LinkData.Type.SYN:
            if sd <= 3: return 1
            return .5
        if rel == LinkData.Type.HYPER or rel == LinkData.Type.HYPO:
            if sd <= 1: return 1
            if sd <= 3: return .5
            return .3
        if rel == LinkData.Type.SIBLING:
            if sd <= 1: return 1
            if sd <= 3: return .3
            if pd <= 1: return .2
            return 0
        return 0
    
    def _reduceGraph(self):
        self._disambiguate()
        self.reduced = True
    
    
class SilberMcCoyChainer(LexGraph):
    """ A linear time lexical chain algorithm as presented by Silber and McCoy.
    Unlike Galley/McKeown, each occurrence of a particular word can have 
    its own sense. 
    """
    class LinkData(LinkData):
        def __init__(self, prevNode, type):
            self.prevNode = prevNode
            LinkData.__init__(self, 0, type)
    
    def __init__(self, data=None, additionalTerms={}):
        LexGraph.__init__(self, data, additionalTerms, wnMaxdist=3)
        
    def _makeLink(self, ln, type, chain=None, lexDist=0):
        """ Set pointer to previous node in chain, create linkdata object.
        @param ln: lex node to be linked
        @param type: relation type
        @param chain: lexical chain ln is to be linked to. Default None: ln is first node in chain.
        @param lexDist: lexical distance between node and chain
        @return: LinkData instance   
        """
        lnPre = None
        if chain:
            "If not -> first node in chain"
            chainLst = chain.asList()
            lnPre = None
            for pos in xrange(-1, -len(chainLst)):
                lnPre, _ = chainLst[pos]
                if lnPre.getWordIndex() != ln.getWordIndex():
                    "We have found a predecessor which is not the same occurrence"
                    break
            
        lnk = SilberMcCoyChainer.LinkData(lnPre, type)
        return lnk
    
    def _scoreLnk(self, ln, lnk, lnOther, lnkOther):
        sdist, pdist = ln.getDist(lnOther)
        return self._getScoreFromMatrix(self._getRelBetweenNodes(ln, lnOther), sdist, pdist)
    
    def _getScoreFromMatrix(self, rel, sd, pd):
        '''  Implementation of scoring matrix given by Silber & McCoy 2000
        @param rel: relation type
        @param sd: sentence dist
        @param pd: paragraph dist 
        @return: float, score
        '''
        if rel == LinkData.Type.IDENT or rel == LinkData.Type.SYN:  return 1
        if rel in (LinkData.Type.HYPER, LinkData.Type.HYPO):
            if sd <= 1: return 1
            return .5
        if rel == LinkData.Type.SIBLING:
            if sd <= 1: return 1
            if sd <= 3: return .3
            if pd == 0: return .2
            return 0
        return 0
        
    def _reduceGraph(self):
        """ Restrict each lex node to the chain it contributes to most - 
        the resulting chains are the final ones.
        
        @return: list of chains - list of lists of LexNodes"""
        chainScores = defaultdict(float)
        toUnlink = []
        for lns in self.wordInstances:
            score = 0.0
            maxScore, maxChain, maxLn = -1, None, None
            for ln in lns:
                "For each lexical node created for a word token, find the highest-scoring chain it is in"
                for chain, link in ln.getMetaChains():
#                    if link.prevNode:
#                        relType = self._getRelBetweenNodes(ln, link.prevNode)
#                        sd, pd = ln.getDist(link.prevNode)
#                        score = self.score(relType, sd, pd)
#                    else:
#                        score = self.score(LinkData.Type.IDENT, 0, 0)
                    """
                    FIXME
                    I am not exactly sure about the scoring here. 
                    The one above takes only the direct predecessor of a node and 
                    would almost always only return chains with identical words in them.
                    I understood Silber/McCoy's paper in that way.
                    
                    The one below adds the scores of all nodes in the chain.
                    This makes more sense IMHO. But still, it seems to be too restrictive.
                    """
                    "For each LN in that chain"
                    for otherLn, otherLink in chain.getLexNodes():
                        "Do not score nodes belonging to the same word token!"
                        if otherLn.getWordIndex() == ln.getWordIndex():    continue
                        score += self._scoreLnk(ln, link, otherLn, otherLink)
                    if score >= maxScore:
                        "Handle ties -- prefer lower WN offsets"
                        if not maxChain or score > maxScore or isinstance(chain.getId(), str) or chain.getId() < maxChain.getId():
                            if maxChain:
                                "Old maxChain"
                                toUnlink.append((maxChain, maxLn))
                            maxScore, maxChain, maxLn = score, chain, ln
                        else:
                            toUnlink.append((chain, ln))
                    else:
                        toUnlink.append((chain, ln))
            log.debug("Picked "+str(maxLn)+" in "+str(maxChain)+" with "+str(maxScore))
            chainScores[chain] += maxScore
            
        for chain, ln in toUnlink:
            log.debug("Unlinking "+str(ln)+" from "+str(chain))
            #chain.unlink(ln)
                
        self.reduced = True 
    
    def _buildChainsAlternative(self):
        '''
        According to Hollingsworth/Teufel 2005:
        Compute total score for each chain, rank chains, remove nodes in strongest chain from all other chains, repeat
        
        TODO
        '''
        chainsToConsider = list(self.chains.itervalues())
        
        maxScore, maxChain = -1, None
        for chain in chainsToConsider:
            score = 0
            for _, lnk in chain:
                score += lnk.score
            "Handle ties -- prefer lower WN offsets"
            if score >= maxScore:
                if not maxChain or score > maxScore or isinstance(chain.getId(), str) or chain.getId() < maxChain.getId():
                    maxScore, maxChain = score, chain
        return [maxChain]
            

def demo():
    """ Computes and prints lexical chains in a sample text (taken from Galley/McKeown 2003) """
    from nltk.tag import pos_tag
    from nltk.tokenize import word_tokenize, sent_tokenize
    
    input = '''Passages from spoken or written text have a quality of unity
    that arises in part from the surface properties of the text; 
    syntactic and lexical devices can be used to create a sense of 
    connectedness between sentences, a phenomenon known as textual cohesion
    [Halliday and Hasan, 1976]. Of all cohesion devices, lexical cohesion is
    probably the most amenable to automatic identification [Hoey, 1991]. 
    Lexical cohesion arises when words are related semantically, 
    for example in reiteration relations between a term and a synonym or superordinate. Lexical chaining is the process of connecting semantically
    related words, creating a set of chains that represent different threads of cohesion through the text. This intermediate representation of text has been used in many natural language processing applications, including automatic summarization [Barzilay and Elhadad, 1997; Silber andMcCoy, 2003], infor- mation retrieval [Al-Halimi and Kazman, 1998], intelligent spell checking [Hirst and St-Onge, 1998], topic segmentation [Kan et al., 1998], and hypertext construction [Green, 1998]
    ''' 
    input = input.replace("-\n","")
    input = sent_tokenize(input)
    input = [[pos_tag(word_tokenize(sent)) for sent in input]]
    mc = GalleyMcKeownChainer(data=input)
    chains = mc.computeChains()
    print "Lexical chains according to Galley/McKeown"
    print "\n".join([str((ch, score)) for ch, score in LexGraph.chainsAsRanked(chains) if len(ch) > 1])
    
    mc = SilberMcCoyChainer(data=input)
    chains = mc.computeChains()
    print "Lexical chains according to Silber/McCoy"
    print "\n".join([str((ch, score)) for ch, score in LexGraph.chainsAsRanked(chains) if len(ch) > 1])
    
if __name__ == "__main__":
    demo()