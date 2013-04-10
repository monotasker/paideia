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
lines = ['Το αὐτου ἐλαιον των Ἑλληνων.',
         'Των Ἑλληνων το ἐλαιον Ἀλεξανδρου.',
         'Το ἐλαιον Ἀλεξανδρου των Ἑλληνων.',
         ]
#'Χαιρε, Ἀλεξανδρος. Τίνος γενου το σου ἐλαιον?',
         #'Χαιρε Ὠ ἀγαθε. Γενου τίνος σου το ἐλαιον?',
         #'Χαιρε! Το ἐλαιον σου γενου τίνος?',
         #'Χαιρε Ἀλεξανδρε. Τίνος το ἐλαιον το σου γενου?',

regex = """
^
(?P<a>((τ|Τ)?ων\s)?Ἑλληνων\s)?
(?P<b>(Ἀλεξανδρου\s|(Α|α)ὐτου\s))?
((Τ|τ)ο\s)?
(?(a)|(?P<c>(Ἀλεξανδρου\s|(Α|α)ὐτου\s)))?
ἐλαιον
(?(b)|(?(c)|(\sἈλεξανδρου|\sαὐτου)))
(?(a)|((\sτων)?\sἙλληνων))\.
$
"""
#^(Χαιρε(ιν)?(,?\s(Ὠ\s)?(Ἀλεξανδρ|ἀγαθ)(ος|ε))?[\.,!]\s)?
#(?P<a>(Γ|γ)ενου\s)?
#(?P<b>(τ|Τ)ίνος\s)?
#(?(a)|(?P<c>γενου\s))?
#(?(b)|(?P<d>τίνος\s))?
#(?P<h>(Σ|σ)ου\s)?
#(?P<f>(Τ|τ)ο\s)?
#(?(h)|(?P<e>σου\s))?
#(ἐ|Ἐ)λαιον
#(?(f)(?P<g>\sτο))?
#(?(h)|(?(e)|\sσου))(?(c)|(?(a)|(?P<i>\sγενου)))?(?(d)|(?(b)|(?P<j>\sτίνος)))?(?(i)|(?(c)|(?(a)|(\sγενου))))(?(j)|(?(d)|(?(b)|(\sτίνος))))\?
#$

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
