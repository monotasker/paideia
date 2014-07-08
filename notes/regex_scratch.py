#! /usr/bin/python
# -*- coding: utf8 -*-
""" Utility script for testing regular expressions in Paideia steps."""
import re
from termcolor import colored
# who should sit πρωτος?

#- Is this word passive or middle (what's its voice)?
#- the parthians came, but the romans are coming
#- are being saved: so when does salvation complete?

# please fetch ἀλλος καρπος
# please fetch ἑτερος καρπος
# proverb, a poor man is seldom strong
# are rich men usually good?
# give this bread to the poor woman
# here all people are equal. The low-born and the noble are brothers and
# sisters.
# here all people are equal. The free man and the slave are brothers.
# here all people are equal. The free woman and the slave(woman) are brothers.
# you should address me as ???
# please give this money to the ptwxos (image)

# greeting is always:.
#(Χαιρε((,)?\s((ὠ|Ὠ)\s)?(Ἀλεξανδρε|καλε|φιλε|γενναιε|κυριε))?[\.,!]\s)?

lines = ['Χαιρε! Θελω ἐννεα προβατους.',
         'Χαιρε, κυριε. Ἐννεα προβατους θελω.'
         ]

regex = r"""
^
(Χαιρε((,)?\s((ὠ|Ὠ)\s)?(Ἀλεξανδρε|καλε|φιλε|γενναιε|κυριε))?[\.,!]\s)?
(?P<a>(?P<b>(Ἐ|ἐ)ννεα\s)(Π|π)ροβατους\s(?(b)|ἐννεα\s))?
(Θ|θ)ελω
(?(a)|(?P<c>\sἐννεα)\sπροβατους(?(c)|\sἐννεα))
\.?
$
"""

^(Χαιρε((,)?\s((ὠ|Ὠ)\s)?(Ἀλεξανδρε|καλε|φιλε|γενναιε|κυριε))?[\.,!]\s)?(?P<a>(?P<b>(Ἐ|ἐ)ννεα\s)(Π|π)ροβατους\s(?(b)|ἐννεα\s))?(Θ|θ)ελω(?(a)|(?P<c>\sἐννεα)\sπροβατους(?(c)|\sἐννεα))\.?$
Greek_only = True

test_regex = re.compile(regex, re.X)
roman_chars = re.compile(u'[\u0041-\u007a]|\d')
print colored(regex, 'cyan')
counter = 1
for l in lines:
    print '==================='
    m = re.match(test_regex, l)
    if m:
        print counter, colored(l, 'green')
    else:
        print counter, colored(l, 'red')
    if Greek_only:
        if re.search(roman_chars, l):
            print colored('roman characters present', 'yellow')
            break
    counter += 1

condensed = re.sub(r'\s', '', regex)
print '==================='
print colored('condensed regex', 'white'), '\n'
print colored(condensed, 'cyan')

goodlist = '|'.join(lines)
print '==================='
print colored('condensed readable answers', 'white'), '\n'
print len(condensed)
print goodlist, '\n\n'
