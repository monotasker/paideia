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

lines = ['Ζητω εἰ ἐχομεν τινας συκα.',
         'Ἐχομεν συκα τινας?',
         'Συκα ζητω.',
         'Τινας ἐχομεν συκα?',
         ]

regex = """
^
(?P<f>Μαρια\s)?
(?P<b>(ζ|Ζ)ητ(ῃ|ει|ω)\s)?
(?(f)|Μαρια\s)?
(?P<c>εἰ\s)?
(?P<e>(Τ|τ)ινας\s)?
((ἐ|Ἐ)χομεν\s)?
(?(e)|(?P<a>τινας\s))?
(Σ|σ)υκα
((a)|\sτινας)?
(?(b)|(?P<d>\sζητω))?
(?(c)(\.)|(?(b)(\.)|(?(d)(\.)|(\?))))
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
print goodlist, '\n\n'
