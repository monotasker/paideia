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
  CSSTransition,
  SwitchTransition
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
    1: ["Alphabet, Nouns, Nominative", "First Words"],
    2: ["Alphabet, Article, Clauses", "Household, Town, Pronouns"],
    3: ["Vocative, Greetings, Word Order", "Exclamations, Conjunctions, Possessives, Demonstratives"],
    4: ["'What' and 'Who' Questions", "Food and Meals"],
    5: ["Genitive, 3rd Declension Stems", "Places and People"],
    6: ["Plural Nominals, Adjectives", "Evaluating, Possessive Adjectives"],
    7: ["Verbs, Present, Accusative, Contract", "Trade and Market, Numbers"],
    8: ["Dative, 'Where', MI Verbs", "Temple and Synagogue"],
    9: ["Passive and Middle", "Movement, Prayer and Worship"],
    10: ["Aorist", "Time, Knowing, the Life Cycle"],
    11: ["Future, Ὁτι, Reporting Speech", "Verbs of Being, Speech and Thought"],
    12: ["Prepositions, Infinitive Clauses, 'How' and 'Why'", "Gifts, Warfare"],
    13: ["Aorist Participles, Genitive Absolute", "Work and Building, Politics"],
    14: ["Present Participles", "Reading, Writing, Cooking, Hosting"],
    15: ["Imperfect, Prepositions, Comparisons", "Health, the Cosmos"],
    16: ["Aorist Passive, Future Passive", "Clothing, Deliveries, Education, Justice"],
    17: ["Adverbs, Relative Clauses", "Body, Athletics"],
    18: ["Subjunctive, Conditional Clauses", "Emotions, Prepositional Prefix"],
    19: ["Perfect", "Names, Religion, Marketplace, Geography"],
    20: ["Optative", "Motion, Power, Knowledge, Perception"]
  }
  const [ loading, setLoading ] = useState(true);

  useEffect(() => {
    if ( !!defaultSet && sets.length != 0) {
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
  // console.log(lessonParam);

  const { user, dispatch } = useContext(UserContext);
  const [lessons, setLessons ] = useState([]);
  // console.log(lessons);

  const [activeLessonId, setActiveLessonId] = useState(
    (!!lessonParam && lessons.length != 0) ? lessons.filter(l => l.lesson_position == lessonParam)[0].id
  : null);
  console.log(activeLessonId);

  const activeLessonSrc = !!activeLessonId ?
    lessons.filter(l => l.id == activeLessonId)[0].video_url.replace("https://youtu.be/", "https://www.youtube.com/embed/")
  : null ;

  const [defaultSet, setDefaultSet ] = useState(!!lessonParam ? parseInt(lessonParam.slice(0, -1)) : user.currentBadgeSet);
  const [loaded, setLoaded] = useState(true);

  useEffect( () => {
    fetchLessons()
    .then(mydata => {
      setLessons(mydata);
      setActiveLessonId(!!lessonParam ?
        mydata.filter(l => l.lesson_position == parseInt(lessonParam))[0].id : null
      );
    });
  }, []);

  useEffect( () => {
    if (!!loaded) {
      let $mask = document.getElementsByClassName("iframe-mask")[0];
      $mask.classList.add("iframe-loaded");
      window.setTimeout($mask.classList.add("mask-done"), 700);
    }
  }, [loaded])

  const setOpenVideo = (event, id) => {
    setLoaded(false);
    setActiveLessonId(id);
  }

  return (
    <Row className="videos-component content-view">
      <Col className="">

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

            <CSSTransition
              in={!activeLessonId}
              timeout={200}
              appear={true}
              classNames="youtube-container"
            >
              <Col className="youtube-container empty">
                <h2>Choose a Lesson</h2>
                <p> Pick a badge set from the list here to see the related video lessons Click on the icon beside each lesson title to see which badges are touched on in the video.</p>
                <p> Beside each lesson title you will also find an icon to download a PDF file with all of the slides from that lesson. This can make a great reference later on. Just don't skip watching through the video first.</p>
              </Col>
            </CSSTransition>

            <SwitchTransition>
              <CSSTransition
                key={activeLessonId}
                timeout={200}
                addEndListener={(node, done) => node.addEventListener("transitionend", done, false)}
                appear={true}
                classNames="youtube-container"
                mountOnEnter={true}
              >
                  <div className="youtube-container">
                    <div className="iframe-mask">
                      <Spinner animation="grow" variant="secondary" />
                    </div>
                    <iframe
                      src={activeLessonSrc}
                      frameBorder="0"
                      onLoad={() => setLoaded(true)}
                      allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowFullScreen
                    >
                    </iframe>
                  </div>
              </CSSTransition>
            </SwitchTransition>

          </Col>
        </Row>

      </Col>
    </Row>
  )
}

export default Videos;
