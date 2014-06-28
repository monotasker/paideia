data = {'title_template': 'tell {}',
        'words1': 'Ἰασων|Σοφια|Φοιβη|Γεωργιος',
        'words2': 'ἀγοραζω|λαμβανω|φερω',
        'words3': 'γαλα|ἐλαιον|ἀρτος|οἰνος',
        'one_prompt_template': ['Ὠ παις! Κελευε της ἀγορας {words3--case@acc}'  # -----
                                '{words2--mood@inf} {words1--case@acc}.',
                                'Ὠ παις! Κελευε {words1--case@acc} '
                                '{words2--mood@inf} {τίς-words3} '
                                '{words3--case@acc} της ἀγορας.',
                                'Ὠ παις! Κελευε {words1--case@acc} '
                                '{words3--case@acc} της ἀγορας '
                                '{words2--mood@inf}.']
        'one_readable_template': [''],
        'one_response_template': [''],
        'one_npcs': 'Maria',
        'one_locations': 'oikos A',
        'one_tags': ['accusative subj. of infinitive',
                'town places',
                'acc personal pronouns',
                'dative of location'],
        'one_tags_extra': [],
        'one_tags_ahead': [],
        'two_prompt_template': ['Χαιρε ὠ [[user]]. Θελει τί Μαρια?',
                                'Χαιρειν. Μαρια θελει τί?',
                                'Χαιρε ὠ [[user]]. Τί Θελει Μαρια?'],  # -------
        'two_response_template': ['((Χαιρε(ιν)?\s)?(ὠ|Ὠ)\s{words1--case@voc_n@2}[,\.!])?'
                                  '(?P<a>(Τ|τ)ῃ ἀγορᾳ)?(?P<c>{words2--mood@imper_n@1_p@2}\s)?(?(a)|?P<b>τῃ ἀγορᾳ\s)?{words3--case@acc}(?(c)|(?P<d>{words2--mood@imper_n@1_p@2}\s))?(?(a)|(?(b)|\sτῃ ἀγορᾳ))(?(c)|(?(d)|{words2--mood@imper_n@1_p@2}\s))[.!]'
                                  ],
        'two_readable_template': ['Ὠ {words1--case@voc_n@2}, {words2--mood@imper_n@1_p@2} '
                                  'τῃ ἀγορᾳ {words3--case@acc}.',
                                  'Ὠ {words1--case@voc_n@2}! Μαρια θελει τῃ ἀγορᾳ σε '
                                  '{words2--mood@inf} {words3--case@acc}.',
                                  'Χαιρε ὠ {words1--mood@voc_n@2}! {words2--mood@imper_n@2} '
                                  'τῃ ἀγορᾳ {words3}.'],
                  'npcs': 'match words1'
                  'locations': 'oikos A',
                  'tags': ['accusative subj. of infinitive',
                           'town places',
                           'acc personal pronouns',
                           'dative of location'],
                  'tags_extra': [],
                  'tags_ahead': []
