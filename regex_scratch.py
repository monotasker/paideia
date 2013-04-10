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

lines = ['Οἱ αὐτου καρποι των Ῥωμαιων.',
         'Των ῥωμαιων οἱ καρποι Ἀλεξανδρου.',
         'Οἱ καρποι Ἀλεξανδρου των Ῥωμαιων.',
         ]

#lines = ['Χαιρε, Ἀλεξανδρος. Τίνος ἐθνους οἱ σου καρποι?',
         #'Χαιρε Ὠ ἀγαθε. Ἐθνους τίνος σου οἱ καρποι?',
         #'Χαιρε! Οἱ καρποι σου ἐθνους τίνος?',
         #'Χαιρε Ἀλεξανδρε. Τίνος οἱ καρποι οἱ σου ἐθνους?',
         #]

#regex = """
#^(Χαιρε(ιν)?(,?\s(Ὠ\s)?(Ἀλεξανδρ|ἀγαθ)(ος|ε))?[\.,!]\s)?
#(?P<a>(Ἐ|ἐ)θνους\s)?
#(?P<b>(τ|Τ)ίνος\s)?
#(?(a)|(?P<c>ἐθνους\s))?
#(?(b)|(?P<d>τίνος\s))?
#(?P<h>(Σ|σ)ου\s)?
#(?P<f>(Ο|ο)ἱ\s)?
#(?(h)|(?P<e>σου\s))?
#(Κ|κ)αρποι
#(?(f)(?P<g>\sοἱ))?
#(?(h)|(?(e)|\sσου))
#(?(c)|(?(a)|(?P<i>\sἐθνους)))?
#(?(d)|(?(b)|(?P<j>\sτίνος)))?
#(?(i)|(?(c)|(?(a)|(\sἐθνους))))
#(?(j)|(?(d)|(?(b)|(\sτίνος))))\?
#$
#"""

regex = """
^
(?P<a>((τ|Τ)?ων\s)?(Ῥ|Ρ|ρ|ῥ)ωμαιων\s)?
(?P<b>(Ἀλεξανδρου\s|(Α|α)ὐτου\s))?
((Ο|ο)ἱ\s)?
(?(a)|(?P<c>(Ἀλεξανδρου\s|(Α|α)ὐτου\s)))?
(κ|Κ)αρποι
(?(b)|(?(c)|(\sἈλεξανδρου|\sαὐτου)))
(?(a)|((\sτων)?\s(ρ|Ῥ|Ρ|ῥ)ωμαιων))\.
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
