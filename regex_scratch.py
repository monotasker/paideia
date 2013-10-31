#! /usr/bin/python
# coding: utf8
import re
from termcolor import colored
# who should sit πρωτος?

# please fetch ἀλλος καρπος
# please fetch ἑτερος καρπος
# proverb, a poor man is seldom strong
# are rich men usually good?
# give this bread to the poor woman
# here all people are equal. The low-born and the noble are brothers and sisters.
# here all people are equal. The free man and the slave are brothers.
# here all people are equal. The free woman and the slave(woman) are brothers.
# you should address me as ???
# please give this money to the ptwxos (image)

# greeting is always:.
#(Χαιρε((,)?\s((ὠ|Ὠ)\s)?(Ἀλεξανδρε|καλε|φιλε|γενναιε|κυριε))?[\.,!]\s)?

#lines = ['Χαιρε. Τίνα πωλῃς?',
        #'Πωλῃς τίνα?',
        #'Χαιρε, ὠ γενναιε. Πωλῃς τίνα?']

#lines = ['Πωλῃ καρπους.',
         #'Πωλῃ τινας καρπους.',
         #'καρπους αὐτος πωλῃ.',
         #'Πωλῃ αὐτος καρπους τινας.',
         #'Τινας καρπους αὐτος πωλῃ.',
         #'Πωλῃ καρπους Ἀλεξανδρος.',
         #]

lines = ['I am giving', 'I usually give', 'I often provide', 'I donate over and over']

regex = """
^
I\s
(am\s((beginning|starting|about|lifting)\sto\s)?)?
(?P<a>repeatedly\s|over\sand\sover\s)?
(?P<b>usually\s|always\s|often\s)?
(donat|giv|provid)(?P<c>e)?(?(c)|ing)?
(?(a)|\s(repeatedly|over\sand\sover))?
(?(b)|\s(usually|always|often))?
\.?
$
"""


#(buy|perceiv(?P<c>e)?)(?(c)|ing)?
#lines = ['You are hearing', 'You usually listen', 'You often hear', 'You listen over and over']

#regex = """
#^
#You\s
#(are\s((beginning|starting|about|going)\sto\s)?)?
#(?P<a>repeatedly\s|over\sand\sover\s)?
#(?P<b>usually\s|always\s|often\s)?
#(hear|listen)(ing)?
#(?(a)|\s(repeatedly|over\sand\sover))?
#(?(b)|\s(usually|always|often))?
#\.?
#$
#"""

#(hear|perceiv(?P<c>e)?)(?(c)|ing)?
#regex = """
#^
#(Χαιρε((,)?\s((ὠ|Ὠ)\s)?(Ἀλεξανδρε|καλε|φιλε|γενναιε|κυριε))?[\.,!]\s)?
#(?P<a>(τ|Τ)(ι|ί)να\s)?
#(π|Π)ωλ(ει|ῃ)(ς|σ)
#(?(a)|\sτ(ι|ί)να)
#(\?)?
#$
#"""

#regex = """
#^
#(?P<c>|(Τ|τ)ινας\s)?
#(?P<b>(Ἀλεξανδρος|(Α|α)ὐτος)\s)?
#(?P<a>(Κ|κ)αρπους\s)?
#(?(c)|(?P<f>τινας\s))?
#(?(b)|(?P<d>(Ἀλεξανδρος|αὐτος)\s))?
#(Π|π)ωλῃ
#(?(d)|(?(b)|(?P<e>\s(Ἀλεξανδρος|αὐτος))))?
#(?(c)|(?(f)|(?P<g>\sτινας)))?
#(?(a)|\sκαρπους)
#(?(c)|(?(f)|(?(g)|\sτινας)))?
#(?(b)|(?(d)|(?(e)|\s(Ἀλεξανδρος|αὐτος))))?
#\.
#$
#"""
#regex = """^(?P<c>|(Τ|τ)ινας\s)?(?P<b>(Ἀλεξανδρος|(Α|α)ὐτος)\s)?(?P<a>(τους\s)?(Κ|κ)αρπους\s)?(?(c)|(?P<f>τινας\s))?(?(b)|(?P<d>(Ἀλεξανδρος|αὐτος)\s))?(Π|π)ωλ(ῃ|ει)(?(d)|(?(b)|(?P<e>\s(Ἀλεξανδρος|ἀυτος))))?(?(c)|(?(f)|(?P<g>\sτινας)))?(?(a)|(\sτους)?\sκαρπους)(?(c)|(?(f)|(?(g)\sτινας)))?(?(b)|(?(d)|(?(e)|\s(Ἀλεξανδρος|αὐτος))))?(\.)?$"""

#regex = """
#^
#(?P<b>Ἀλεξανδρος\s)?
#(?P<e>(Σ|σ)κευον\s)?
#(?P<a>((Ἐ|ἐ)λαιον\s|(Ἐ|ἐ)λαιου\s))?
#(?(e)|(?P<g>(Σ|σ)κευον\s))?
#(Π|π)ωλῃ
#(?(g)|(?(e)|(?P<h>\sσκευον)))?
#(?(b)|(?P<d>\sἈλεξανδρος))?
#(?(h)|(?(g)|(?(e)|(?P<i>\sσκευον))))?
#(?(a)|(\sἐλαιον|\sἐλαιου))
#(?(i)|(?(h)|(?(g)|(?(e)|(?P<j>\sσκευον)))))?
#(?(d)|(?(b)|\sἈλεξανδρος))?
#(?(j)|(?(i)|(?(h)|(?(g)|(?(e)|(Σ|σ)κευον)))))?
#\.
#$
#"""


Greek_only = False

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
