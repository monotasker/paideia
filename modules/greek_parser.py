import re

def tokenize(str):
    	"""
     Divide a string into clauses and each clause into word tokens.

     Returns a list of OrderedDicts, each of which represents one clause (or fragment). 
			 The keys in each dict are the tokens which make up the clause, ordered according 
			to their appearance in the string.
     """
     clauses = re.split(str, r'[\.\?;:,]')
     tokenized = []
     for c in clauses:
        token_dict = OrderedDict(t: None for t in c.split(' '))
        tokenized.append(token_dict)
     return tokenized


class Parser(object):
		""" 
		Abstract class defining basic recursive parsing behaviour.
   """

def __init__(self, string, *structures):
    """ """
    self.string = string
    self.structures = [s for s in structures]

def validate(self, tokens)
     """
     compare list of word tokens to definition of valid natural language expressions. 

      clause should be Clause() object
     """
			for s in self.structures:
         tokens, match, words = s.validate(tokens)
         if not tokens:
             return False
     
			if match:
         tokens, match, new_words = self.match_string(tokens)
						words.extend(new_words)

			if match:
     			tokens, match = self.test_order(tokens, words)

			self.words = words

     return (tokens, match, words)

def match_string(self, tokens):
		 '''
		 '''
		 classname = type(self).__name__
		 test = re.compile(self.string)
		 tokens_free = [t[0] for t, v in tokens if len(t) == 1]
    tokenstring = ' '.join(tokens_free) 
			mymatch =	 test.search(tokenstring, re.U|re.I)
			mygroups = set(mymatch.groups())
			result = False
			words = []
			if mygroups and len(mygroups) > 1:
					for g in mygroups:
							try:
									i = index((g), tokens)
									tokens[i] = (g, classname)
									words += (classname, g, i)
							except Exception:
									inds = [index(m, tokens) for m in tokens if m[0] == g]
									for i in inds:
										 tokens[i] = (g, classname)
											words += (classname, g, i)
							result = True
			elif mygroups and len(mygroups) == 1:
 					i = index((mygroups[0]), tokens)
					tokens[i] = (g, classname)
					words += (classname, g, i)
					result = True
			else:
					pass
			return (tokens, result, words)

def test_order(self, tokens, words):

			pass

class Clause(Parser):

			def test_order(self, tokens) 


class NounPhrase(Parser):

	  def test_order(self, tokens, words):
				art = [w for w in words if w[0] == 'Art']
				cnom = [w for w in words if w[0] == 'CNom']
				pnom = 
				adj

				[Art.once(), cnom, art.before(CNom)]
				[art.twice, cnom, art.before_after(cnom), adj, art.before(adj)]
				[art.once, pnom, art.after(pnom), art.before(adj)]

				super
						
							
						
				
