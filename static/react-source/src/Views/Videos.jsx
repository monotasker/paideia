import React, { useState, useContext, useEffect, useLayoutEffect } from "react";
import { useParams } from "react-router-dom";
import {
  Row,
  Col,
  Accordion,
  Card,
  Button,
  ListGroup,
  Spinner
} from "react-bootstrap";
import {
  CSSTransition
} from "react-transition-group";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { UserContext } from "../UserContext/UserProvider";
import { fetchLessons } from "../Services/stepFetchService";

const LessonList = ({defaultSet, lessons, setVideoHandler, activeLesson}) => {
  const setnums = lessons.map(
    item => parseInt(item.lesson_position.toString().slice(0, -1))
  );
  const sets = [...new Set(setnums.filter(i => !!i))];
  const setTitles = {
    1: ["Alphabet, Nouns, and Nominative Case", "First Words"],
    2: ["Alphabet (again), Article, Clauses", "Words for Household and Town, Pronouns"],
    3: ["Vocative Case, Greetings, Word Order", "Exclamations and Conjunctions, Possessives, Demonstratives"],
    4: ["'What' and 'Who' Questions", "Words for Food and Meals"],
    5: ["Genitive Case, 3rd Declension Stems", "Words for Places and People"],
    6: ["Plural Nominals, Adjectives", "Words for Evaluating, Possessive Adjectives"],
    7: ["Verbs, Present Tense, Accusative Case, Contract Verbs", "Words for Trade and Market, Numbers"],
    8: ["Dative Case, 'Where' Questions, MI Verbs", "Words for Temple and Synagogue"],
    9: ["Passive and Middle Voices", "Words for Movement, Prayer and Worship"],
    10: ["Aorist Tense", "Words for Time, Knowing, the Life Cycle"],
    11: ["Future Tense, Ὁτι Clauses, Reporting Speech", "Verbs of Being, Words for Speech and Thought"],
    12: ["Prepositions, Infinitive Clauses, 'How' and 'Why' Questions", "Words for Gifts, Warfare"],
    13: ["Aorist Participles, Genitive Absolute", "Words for Work and Building, Politics"],
    14: ["Present Participles", "Words for Reading and Writing, Cooking and Hosting"],
    15: ["Imperfect Tense, Prepositions (again), Comparisons", "Words for Health, the Cosmos"],
    16: ["Aorist Passive, Future Passive", "Words for Clothing and Deliveries, Education, Justice"],
    17: ["Adverbs, Relative Clauses", "Words for the Body, Athletics"],
    18: ["Subjunctive Mood, Conditional Clauses", "Words for Emotions, Prepositional Prefix Words"],
    19: ["Perfect Tense", "Prominent Names, Words for Religion, Marketplace, Geography"],
    20: ["Optative Mood", "Words for Motion (again), Power, Knowledge and Perception"]
  }
  const [ loading, setLoading ] = useState(true);

  useEffect(() => {
    console.log(defaultSet);
    console.log(sets);
    console.log(sets.includes(defaultSet));
    console.log(defaultSet != 0 && sets.length != 0);

    if ( defaultSet != 0 && sets.length != 0) {
      const $myCard = document.getElementById(`badgeset_header_${defaultSet}`);
      $myCard.scrollIntoView();
    }
  }, [lessons]);

  return  (
    <Accordion defaultActiveKey={!!defaultSet ? defaultSet : 0}>
      { !!sets && sets.map(myset =>
        <Card key={`badgeset_header_${myset}`} id={`badgeset_header_${myset}`}>
          <Card.Header>
            <Accordion.Toggle as={Button} variant="link" eventKey={myset}>
              <span className="lessonLink-set">{`Badge set ${myset}`}</span><br />
              <span className="lessonLink-grammar"><FontAwesomeIcon icon="lightbulb" />{setTitles[myset][0]}</span><br />
              <span className="lessonLink-vocab"><FontAwesomeIcon icon="sort-alpha-down" />{setTitles[myset][1]}</span>
            </Accordion.Toggle>
          </Card.Header>
          <Accordion.Collapse eventKey={myset}>
            <Card.Body>
              <ListGroup>
                {lessons.filter(l => l.lesson_position.toString().slice(0, -1) == myset.toString()).map(i =>
                    <ListGroup.Item key={i.title}
                      active={i.id == activeLesson ? true : false}
                      action
                      onClick={e => setVideoHandler(e, i.id)}
                    >
                      {i.title}

                    </ListGroup.Item>
                )}
              </ListGroup>
            </Card.Body>
          </Accordion.Collapse>
        </Card>
      )}
    </Accordion>
  )
}


const Videos = (props) => {

  const { lessonParam } = useParams();
  console.log(lessonParam);

  const { user, dispatch } = useContext(UserContext);
  const [lessons, setLessons ] = useState([]);
  console.log(lessons);

  const [activeLessonId, setActiveLessonId] = useState(
    (!!lessonParam && lessons.length != 0) ? lessons.filter(l => l.lesson_position == lessonParam)[0].id
    : null
  );
  console.log("activeLessonId");
  console.log(activeLessonId);

  const activeLessonSrc = !!activeLessonId ?
    lessons.filter(l => l.id == activeLessonId)[0].video_url.replace("https://youtu.be/", "https://www.youtube.com/embed/")
  :
    null
  ;

  const [defaultSet, setDefaultSet ] = useState(!!lessonParam ? parseInt(lessonParam.slice(0, -1)) : user.currentBadgeSet);
  const [loaded, setLoaded] = useState(true);

  useEffect( () => {
    fetchLessons()
    .then(mydata => {
      setLessons(mydata);
      console.log(mydata);

      setActiveLessonId(!!lessonParam ?
        mydata.filter(l => l.lesson_position == parseInt(lessonParam))[0].id
        : 0
      );
    });
  }, []);

  useEffect( () => {
    setLoaded(!loaded ? true : false);
  }, [activeLessonId])

  const setOpenVideo = (event, id) => {
    setLoaded(false);
    setActiveLessonId(id);
  }

  return (
    <Row className="videos-component content-view">
      <Col className="">
      <h2>Video Lessons</h2>


        <Row className="lessons-display-container horizontal">
          <Col xs={{span: 12, order: 2}} md={{span: 4, order: 1}}
            className="lessonlist"
          >
            { lessons.length != 0 &&
            <LessonList
              defaultSet={defaultSet}
              lessons={lessons}
              setVideoHandler={setOpenVideo}
              activeLesson={activeLessonId}
            />
            }
          </Col>

          <Col xs={{span: 12, order: 1}} md={{span: 8, order: 2}}
            className="video-display"
          >
            <div className="video-mask">
              <Spinner animation="grow" variant="secondary" />
            </div>

            <CSSTransition
              in={!activeLessonId}
              timeout={500}
              appear={true}
              classNames="youtube-container"
              mountOnEnter={true}
              unmountOnExit={true}
            >
              <div className="youtube-container empty">Choose a Lesson
              Pick a badge set from the list here to see the related video lessons Click on the icon beside each lesson title to see which badges are touched on in the video.

              Beside each lesson title you will also find an icon to download a PDF file with all of the slides from that lesson. This can make a great reference later on. Just don\'t skip watching through the video first.
              </div>
            </CSSTransition>

            <CSSTransition
              in={!!loaded}
              timeout={2000}
              appear={true}
              classNames="youtube-container"
              mountOnEnter={true}
              unmountOnExit={true}
            >
                <div className="youtube-container">
                  <iframe
                    src={activeLessonSrc}
                    frameBorder="0"
                    allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowFullScreen
                  >
                  </iframe>
                </div>
            </CSSTransition>

          </Col>
        </Row>

      </Col>
    </Row>
  )
}

export default Videos;
