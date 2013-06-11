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
#(Χαιρε(\s((ὠ|Ὠ)\s)?(Ἀλεξανδρε|καλε|φιλε|γενναιε|κυριε))?[\.,!]\s)?

lines = ['Πωλει ἐλαιον.',
         'Ἐλαιου πωλει σκευον.',
         'Πωλει ἐλαιου σκευον Ἀλεξανδρος.',
         ]

regex = """
^
(?P<b>Ἀλεξανδρος\s)?
(?P<e>(Σ|σ)κευον\s)?
(?P<a>((Ἐ|ἐ)λαιον\s|(Ἐ|ἐ)λαιου\s))?
(?(e)|(?P<g>(Σ|σ)κευον\s))?
(Π|π)ωλει
(?(g)|(?(e)|(?P<h>\sσκευον)))?
(?(b)|(?P<d>\sἈλεξανδρος))?
(?(h)|(?(g)|(?(e)|(?P<i>\sσκευον))))?
(?(a)|(\sἐλαιον|\sἐλαιου))
(?(i)|(?(h)|(?(g)|(?(e)|(?P<j>\sσκευον)))))?
(?(d)|(?(b)|\sἈλεξανδρος))?
(?(j)|(?(i)|(?(h)|(?(g)|(?(e)|(Σ|σ)κευον)))))?
\.
$
"""


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
