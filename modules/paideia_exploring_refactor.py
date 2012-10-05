from gluon import current
from datetime import datetime, timedelta
from itertools import chain
#from gluon.storage import Storage

class Stance(object):

    def __init__(self, db=None, session=None, user=None, tag_progress=None, npcs=None):
        '''
        Constructor for Stance class
        '''
        # timestamp the Stance instance so that we can check for expiration
        self.start_time = datetime.utcnow()
        # get session object
        # TODO: can we get this here or do we need to get it in the method?
        if session is None:
            self.session = current.session['stance']
        else:
            self.session = session

        if user is None:
            auth = current.auth
            user = auth.user_id

        # user's rank in the badge progression
        if tag_progress is None:
            tag_progress = db(db.tag_progress.name == self.user).select().first()
        self.rank = self._get_rank(self.user, tag_progress)

        if npcs is None:
            npcs = db(db.npcs.id > 0).select()
        self.npcs = npcs

        if db is None:
            db = current.db

    def _is_stale(self,
                  start_time,
                  tz=None,
                  lifetime=timedelta(days=1)):
        '''
        Checks to see whether this Stance instance is still valid or whether
        a new one needs to be instantiated (based on the date it was created).
        The default lifetime is the current 24-hour day (user's local time)
        '''
        if tz is None:
            tz = self.tz

    def _get_user(self):
        '''
        Returns the id of the current user
        '''
        return self.user

    def _get_npc(self, npcs):
        '''
        Returns one npc object
        '''
        pass

    def _get_rank(self, tag_progress):
        '''
        Return the specified user's rank as stored in the tag_progress table.
        '''
        if tag_progress is None:
            rank = 1
        else:
            rank = tag_progress.latest_new
            if rank == 0:
                tag_progress.update_record(latest_new=1)
                rank = 1

        return rank

    def _store_in_session(self, session):
        '''
        Store the Stance instance in the web2py session object for retrieval
        on the next http request. This is the chief mechanism used for data
        persistence for a given user.
        '''
        try:
            session['Stance'] = self
        except Exception, e:
            print type(e), e

    def _store_in_db(self, user, db):
        '''
        Store the Stance instance in the database to allow for retrieval (and
        data persistence) across different browser sessions or even different
        browsers.
        '''
        try:
            db(db.session_data.user == user).update_or_insert()
        except Exception, e:
            print type(e), e

class Categories(object):

    def __init__(self, user=None, tags=None, tag_records=None, rank=None):
        '''
        Constructor
        '''
        if self.verbose: print 'calling Walk._categorize_tags--------------'
        # inject default dependencies
        if user is None:
            auth = current.auth
            self.user = auth.user_id
        else:
            self.user = user
        if tag_records is None:
            db = current.db
            self.tag_records = db(db.tag_records.id > 0).select()
        else:
            self.tag_records = tag_records
        if tags is None:
            self.tags = db(db.tags.id > 0).select()
        else:
            self.tags = tags
        if rank is None:
            pass

    def get_categories(self):
        '''
        Master method (public) to categorize tags for the specified user
        based on performance and time.

        called by Stance.__init__() and by Stats
        '''
        categories = dict((x, []) for x in xrange(1, 5))
        record_list = [tr for tr in self.tag_records if tr['name'] == self.user]

        # default starting categories for new user
        if len(record_list) > 1:
            categories = self._first_cat_set(categories)
        # otherwise base categories on user performance
        else:
            # get user's tag_records rows and remove any duplicate entries
            # combine values in the process of removal and update db as
            # necessary
            record_list = self._remove_dups(record_list)
            # here is the core spaced repetition algorithm
            categories = self._sort_by_date(categories, record_list)
            rank = self._get_rank(self.user)
            categories = self._add_untried_tags(rank, categories, self.tags)
            categories = self._remove_dups2(categories, rank)
            # If there are no tags needing immediate review, introduce new one
            if not categories[1]:
                categories[1] = self._introduce()

        return categories



    def _remove_dups(self, record_list):
        '''
        Identify duplicate record_list rows for this user and delete them from
        the db.
        '''
        discrete_tags = set([t['tag'] for t in record_list])
        if len(record_list) > len(discrete_tags):
            for tag in discrete_tags:
                shortlist = record_list.find(lambda row: row.tag == tag)
                if len(shortlist) > 1:
                    for record in shortlist[1:]:
                        db.tag_records[record.id].delete()
        # actually filter out duplicates from the supplied record_list so that
        # a second db call is not necessary - return that filtered set
        new_record_list = None

        return new_record_list

    def _first_cat_set(self, categories):
        '''
        Provide a new user with a category set in which cat1 has all of the
        tags with a position value of 1.
        '''
        firsttags = [t.id for t in db(db.tags.position == 1).select()]
        categories[1] = firsttags
        view_slides = firsttags

        return {'categories': categories, 'view_slides': view_slides}

    def _sort_by_date(self, categories, record_list):
        '''
        Sort attempted tags into categories based on performance and time
        intervals.
        '''
        for record in record_list:
            # TODO: Make sure there's only one record per person, per tag
            #get time-based statistics for this tag
            #note: arithmetic operations yield datetime.timedelta objects
            now_date = datetime.utcnow()
            right_dur = now_date - record.tlast_right
            right_wrong_dur = record.tlast_right - record.tlast_wrong

            # Categorize q or tag based on this performance
            # spaced repetition algorithm for promotion from cat1
            if ((right_dur < right_wrong_dur)
                    # don't allow promotion from cat1 within 1 day
                    and (right_wrong_dur > datetime.timedelta(days=1))
                    # require at least 10 right answers
                    and (record.times_right >= 20)) \
                or ((record.times_wrong > 0)  # prevent zero division error
                    and (record.times_right / record.times_wrong) >= 10):
                   # allow for 10% wrong and still promote

                if right_wrong_dur.days >= 7:
                    if right_wrong_dur.days > 30:
                        if right_wrong_dur > datetime.timedelta(days=180):
                            category = 1  # Not due or tried for 6 months
                        else:
                            category = 4  # Not due, delta > a month
                    else:
                        category = 3  # delta between a week and month
                else:
                    category = 2  # Not due but delta is a week or less
            else:
                category = 1  # Spaced repetition requires review
            categories[category].append(record.tag.id)

        return categories

    def _add_untried_tags(self, rank, categories, tags):
        '''
        Check for tags that don't yet have a tag_records entry because the user
        hasn't tried them yet. If present, add these to category 1.
        '''
        #check for untried in current and all lower ranks
        #should only be necessary until junk data is fixed?
        left_out = []
        for r in range(1, rank + 1):
            newtags = [t.id for t in db(db.tags.position == r).select()]
            alltags = list(chain(*categories.values()))
            left_out.extend([t for t in newtags if t not in alltags])
        if left_out:
            categories[1].extend(left_out)

        return categories

    def _remove_dups2(self, categories, rank):
        '''
        Remove duplicate tag id's from each category
        Make sure each of the tags is not beyond the user's current ranking
        even if some were actually tried before (through system error)
        '''
        for k, v in categories.iteritems():
            if v:
                newv = [t for t in v if db.tags[t].position <= rank]
                categories[k] = list(set(newv))

        return categories



class Npc(object):

    def __init__(self, npc_id=None):

        db, session = current.db, current.session

        if npc_id is not None:
            self.npc = db.npcs(npc_id)
            self.image = self._get_image(self.npc)

            self._save_session_data()

        else:
            self._get_session_data()
            info = self._get_session_data()
            self.npc = info.npc
            self.image = info.image
            self.location = info.location

    def _save_session_data(self):
        '''
        Save attributes in session.
        '''
        session = current.session

        session_data = {}
        session_data['npc'] = self.npc.id
        session_data['npc_image'] = self.image

        session.walk.update(session_data)

    def _get_session_data(self):
        '''
        Get the walk attributes from the session.
        '''

        db, session = current.db, current.session

        if 'npc' in session.walk:
            npc = db.npcs(session.walk['npc'])
            image = session.walk['npc_image']
        else:
            npc = None
            image = None

        location = session.walk['active_location']

        return {'image': image, 'npc': npc, 'location': location}

    def _get_image(self, row):
        '''
        Get the image to present as a depiction of the npc.
        '''
        debug = False
        db = current.db

        if debug: print row
        try:
            url = URL('static/images', db.images[row.npc_image].image)
            if debug:
                print url
            # TODO: Add title attribute
            return IMG(_src=url)
        except:
            print 'Npc._get_image(): Could not find npc image'
            return
