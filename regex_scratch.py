#!/usr/bin/python
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
lines = [
        'Ταπεινοι οἱ δουλοι ἡμων.',
        'Οἱ ἡμων δουλοι ταπεινοι.',
        'Ἡμων οἱ δουλοι ταπεινοι.',
        'Ταπεινοι ἡμων οἱ δουλοι.',
        'Ταπεινοι οἱ δουλοι ἡμων.',
        'Οἱ δουλοι ἡμων ταπεινοι.',
        'Οἱ ἡμων δουλοι ταπεινοι.',
        'Οἱ δουλοι ἡμων ταπεινοι.'
        ]

regex = """^
(?P<a>(τ|Τ)απεινοι\s)?
(?P<d>(Ἡ|ἡ)μων\s)?
(?P<g>(Ο|ο)ἱ\s)?
(?(d)|(?P<c>(Ἡ|ἡ)μων\s))?
(δ|Δ)ουλοι
(?(c)|(?(d)|\sἡμων))
(?(a)|\sταπεινοι)
\.$"""

test_regex = re.compile(regex, re.X)
print colored(regex, 'cyan')
for l in lines:
    print '==================='
    m = re.match(test_regex, l)
    if m:
        print colored(l, 'green')
    else:
        print colored(l, 'red')

condensed = re.sub(r'\s', '', regex)
print '==================='
print colored('condensed regex', 'white'), '\n'
print colored(condensed, 'cyan')

goodlist = '|'.join(lines)
print '==================='
print colored('condensed readable answers', 'white'), '\n'
print goodlist, '\n\n'


