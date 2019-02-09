from pprint import pprint
if 0:
    from gluon import current, MARKMIN, SQLFORM
    request, session, db = current.request, current.session, current.db
    response, auth = current.response, current.auth
# import traceback
from datetime import datetime, timedelta
from itertools import chain
from plugin_markmin_extras import mm_extras


def decklist():
    """
    Returns a dictionary of information on decks for each tag set.

    The dictionary keys are integers representing set numbers. The values
    are 2 member tuples with these members:
        [0]     a boolean (True/False) indicating whether the set is
                active for the current user;
        [1]     a list of dictionaries each representing one slide deck.
    the keys:values for each deck dictionary are:
        [name]          the title of the slide deck
        [classes]       a string giving relevant html "class" values
        [tags]          a list of tuples for the tags associated with the
                            slide deck.
    each deck tuple includes three members:
        [0]     the id of the tag (NOT the badge id)
        [1]     the name of the associated badge (NOT the tag name)
        [2]     the "position" of the tag in the set progression.
    # TODO: this position value is redundant
    # TODO: add the badge description string
    # TODO: add the id of each deck

    Decks that have been changed less than 7 days ago are given a class of
    "plugin_slider_new " to allow flagging or distinct theming via css.
    """
    decks = db(db.plugin_slider_decks.id > 0).select()
    deckstags = {}
    for d in decks:
        tagbadges = db((db.tags.id == db.badges.tag) &
                       (db.tags.slides.contains(d.id))).select()
        decktags = [(int(t.tags.id),
                     t.badges.badge_name,
                     int(t.tags.tag_position)) for t in tagbadges]
        deckstags[d.id] = decktags
    # the 999 constraint allows position 999 to be used to deactivate
    maxpos = max([int(t[2]) for d in list(deckstags.values()) for t in d
                  if int(t[2]) > 0 and int(t[2]) < 999])
    setslist = {}
    prog = db(db.tag_progress.name == auth.user_id).select().first()
    for i in range(0, maxpos):
        setids = list(set([int(did) for did, dtags in deckstags.items()
                             if i in [t[2] for t in dtags]
                             and did not in chain(setslist)]))
        setids = sorted(setids,
                        key=lambda sd: db.plugin_slider_decks(sd).deck_position)
        if setids:
            setdecks = []
            for did in setids:
                drow = db.plugin_slider_decks(did)
                dinfo = {'id': did,
                         'name': drow.deck_name,
                         'tags': deckstags[did],
                         'classes': ''}
                now = datetime.utcnow()
                week = timedelta(days=7)
                if drow.updated and (now - drow.updated < week):
                    dinfo['classes'] = 'plugin_slider_new '
                setdecks.append(dinfo)
            active = True if prog and i <= prog.latest_new else False
            setslist[i] = (active, setdecks)
        else:
            pass
    return setslist


def start_deck():
    """
    Initiate showing a plugin_slider slideshow.

    Initialize (create or reset to default) the following session variables
    to control slideshow display:
        plugin_slider_did (int): The id of the current deck
            (from db.plugin_slider)
        plugin_slider_deckorder (list of ints): a list holding the ids of all
            slides in the current deck in their default display order
            of the user's viewing history. This is to allow "back"
            functionality within the deck, particularly if the user jumps
            between slides in a non-default order.

    Send data to view start_deck.load to build the slideshow frame. Then
    call show_slide() to display the first slide of the deck.

    Takes no parameters.
    Expects the first url argument to be the id of the deck to be initialized.
    """
    if len(request.args):
        did = int(request.args[0])
    # elif 'plugin_slider_did' in session.keys():
        # did = session.plugin_slider_did
    else:
        did = None
    session.plugin_slider_did = did
    dname = None
    firstslide = request.vars.firstslide if 'firstslide' in list(request.vars.keys()) else None
    theme = None
    deckorder = None
    if did:
        session['plugin_slider_did'] = did
    else:
        response.flash = "Sorry, I couldn't find the slides you asked for."

    if did:
        deck = db.plugin_slider_decks(did)
        dname = deck.deck_name
        deckorder = [s for s in deck.deck_slides if s is not None]
        if deckorder and len(deckorder) > 0:
            session['plugin_slider_deckorder'] = deckorder
            firstslide = deckorder[0] if not firstslide else firstslide
            theme = db.plugin_slider_themes[deck.theme[0]].theme_name
        else:
            response.flash = "Sorry, I couldn't find any slides for that deck."

    # get lists for nav interface
    mydecklist = decklist()
    # slidelist = slidelist()

    if not firstslide:
        response.flash = "Sorry, there aren't any slides in that deck yet."

    return dict(did=did,
                dname=dname,
                firstslide=firstslide,
                theme=theme,
                setslist=mydecklist,
                # slidelist=slidelist,
                deckorder=deckorder)


def slidelist():
    """
    """
    pass
    '''
    # slidelist = UL(_class='plugin_slider_decklist')
    # badgetags = db((db.tags.slides.contains(theslide.id)) &
                   #(db.badges.tag == db.tags.id)).select()
    # for d in deckorder:
        # theslide = db.plugin_slider_slides[d]
        # decklist.append(LI(A(theslide.slide_name,
                            # _href=URL('plugin_slider',
                                      # 'show_slide',
                                      # args=[theslide.id]),
                            # cid='plugin_slider_slide')))
        # for b in badges:
            # decklist[-1].append(SPAN(b.badges.badge_name))
    # deckmenu = None
    '''


def show_slide():
    """
    Assemble and return content of a single slide.

    Takes only one parameter, 'slidearg', an int containing the id of the
    slide to be displayed. This defaults to None. If it is not present
    the function looks for the first URL argument to provide the slide id.

    Returns a dictionary with a single item, 'content', containing a
    web2py MARKMIN helper object with the text contents of the slide.
    """
    deckorder = request.vars.deckorder if 'deckorder' in list(request.vars.keys()) \
                else session.plugin_slider_deckorder
    if len(request.args) > 1:
        sid = int(request.args[1])
    elif 'firstslide' in list(request.vars.keys()):
        sid = int(request.vars.firstslide)
    else:
        sid = session.plugin_slider_sid
    session.plugin_slider_sid = sid

    did = int(request.args[0]) if len(request.args) else session.plugin_slider_did
    session.plugin_slider_did = did
    dname = db.plugin_slider_decks(did).deck_name

    # get slide content
    slide = db.plugin_slider_slides[int(sid)]
    images = db(db.images.id > 0).select().as_list()
    audios = db(db.audio.id > 0).select().as_list()
    # filename, stream = db.plugin_slider_slides.pdf.retrieve(slide.image)
    pdf = slide.pdf
    # markmin extensions from plugin_markmin_extras
    content = MARKMIN(slide.slide_content, extra=mm_extras)

    return dict(content=content,
                pdf=pdf,
                did=did,
                dname=dname,
                sid=sid,
                editform=editform(),
                deckorder=deckorder)


def addform():
    """
    Return a sqlform object for editing the specified slide.
    """
    did = request.args[0]
    direction = request.vars.direction
    sid = session.plugin_slider_sid
    deckorder = session.plugin_slider_deckorder
    # get index for inserting new slide
    sindex = deckorder.index(sid)
    newindex = sindex + 1
    if newindex == len(deckorder) or direction == 'before':
        newindex = sindex

    form = SQLFORM(db.plugin_slider_slides,
                   separator='',
                   deletable=True,
                   showid=True,
                   formname='plugin_slider_slides/addnew')
    if form.process(formname='plugin_slider_slides/addnew').accepted:
        deckrow = db.plugin_slider_decks(did)
        # TODO: is this the best way to get the new slide id?
        slideid = db(db.plugin_slider_slides).select().last().id
        deckslides = deckrow.deck_slides
        deckslides.insert(sindex, slideid)
        deckrow.update_record(deck_slides=deckslides)
        response.flash = 'The new slide was added successfully.'
    elif form.errors:
        print('\n\nlistandedit form errors:')
        pprint({k: v for k, v in form.errors.items()})
        print('\n\nlistandedit form vars')
        pprint({k: v for k, v in form.vars.items()})
        print('\n\nlistandedit request vars')
        pprint({k: v for k, v in request.vars.items()})
        response.flash = 'Sorry, there was an error processing ' \
                         'the form. The changes have not been recorded.'

    else:
        pass

    return form


def delete_slide():
    """
    Delete the slide from the deck and display the previous existing slide.
    """
    did = request.args[0]
    sid = request.args[1]
    deckorder = session.plugin_slider_deckorder

    deckrow = db.plugin_slider_decks(did)
    sliderow = db(db.plugin_slider_slides.id == sid).select().first()

    if deckrow and sliderow:
        sliderow.delete_record()
        if db.plugin_slider_slides(sid):
            print('slide', sid, 'still in db')
        sindex = deckorder.index(int(sid))
        deckorder.pop(sindex)
        deckrow.update_record(deck_slides=deckorder)

        fallback_index = sindex - 1 if sindex != 0 else sindex
        session.plugin_slider_sid = fallback_id = deckorder[fallback_index]
        session.plugin_slider_deckorder = deckorder
    else:
        response.flash = 'Sorry, I couldn\'t delete the slide.'

    return {'did': did,
            'sid': fallback_id}


def editform():
    """
    Return a sqlform object for editing the specified slide.
    """
    sid = session.plugin_slider_sid
    form = SQLFORM(db.plugin_slider_slides, sid,
                   separator='',
                   deletable=True,
                   showid=True)

    if form.process(formname='plugin_slider_slides/{}'.format(sid)).accepted:
        response.flash = 'The changes were recorded successfully.'
    elif form.errors:
        print('\n\nlistandedit form errors:')
        pprint({k: v for k, v in form.errors.items()})
        print('\n\nlistandedit form vars')
        pprint({k: v for k, v in form.vars.items()})
        print('\n\nlistandedit request vars')
        pprint({k: v for k, v in request.vars.items()})
        response.flash = 'Sorry, there was an error processing ' \
                         'the form. The changes have not been recorded.'

    else:
        pass

    return form


def next_slide():
    """
    Present the next slide in a deck sequence.

    Find the next slide's id and redirect to show_slide to display its content.
    If already at the last slide, simply present the current slide again and
    give the user a response.flash message.

    """
    sid = session.plugin_slider_sid
    deckorder = session.plugin_slider_deckorder
    curr_i = deckorder.index(int(sid))
    new_i = curr_i + 1
    if len(deckorder) > new_i:
        session.plugin_slider_sid = deckorder[new_i]
    else:
        response.flash = 'You are already at the last slide.'
    return show_slide()


def prev_slide():
    """
    Find the previous slide in a deck sequence and redirect to
    show_slide to display its content. If already at the first slide,
    simply present it again and give the user a response.flash message.
    """

    sid = session.plugin_slider_sid
    deckorder = session.plugin_slider_deckorder
    curr_i = deckorder.index(int(sid))
    new_i = curr_i - 1
    if new_i >= 0:
        session.plugin_slider_sid = deckorder[new_i]
    else:
        response.flash = 'You are already at the last slide.'
    return show_slide()
