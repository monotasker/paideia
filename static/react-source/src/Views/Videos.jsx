import React,
       { useState,
         useContext,
         useEffect,
         useLayoutEffect,
         useMemo
       } from "react";
import { useParams
} from "react-router-dom";
import {
  Row,
  Col,
  Accordion,
  Card,
  Button,
  ListGroup,
  Spinner,
  ResponsiveEmbed
} from "react-bootstrap";
import {
  CSSTransition,
  SwitchTransition
} from "react-transition-group";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { UserContext } from "../UserContext/UserProvider";
import { fetchLessons } from "../Services/stepFetchService";
import { urlBase } from "../variables";

const LessonList = ({defaultSet, lessons, setVideoHandler, activeLesson}) => {
  const setnums = useMemo(() => lessons.map(
    item => parseInt(item.lesson_position.toString().slice(0, -1))
    ), [lessons]
  );
  const sets = useMemo(() => [...new Set(setnums.filter(i => !!i))],
    [setnums]
  );
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
  // const [ loading, setLoading ] = useState(true);

  useEffect(() => {
    if ( !!defaultSet && sets.length !== 0) {
      const $myCard = document.getElementById(`badgeset_header_${defaultSet}`);
      $myCard.scrollIntoView();
    }
  }, [lessons, defaultSet, sets]);

  // const downloadPdf = (filename) => {
  //   downloadFile({ filename: filename })
  //   .then(info => {
  //       console.log(info);
  //   });
  // }

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
                {lessons.filter(l => l.lesson_position.toString().slice(0, -1) === myset.toString()).map(i =>
                    <ListGroup.Item key={i.title}
                      active={i.id === activeLesson ? true : false}
                      action
                      onClick={e => setVideoHandler(e, i.id)}
                    >
                      {i.title}
                      <a className="lesson-list-item-pdf"
                        href={`/${urlBase}/api/download/${i.pdf}`}
                      >
                        <FontAwesomeIcon icon="file-pdf" />
                      </a>

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
  // console.log(`lessonParam: ${lessonParam}`);
  const { user, dispatch } = useContext(UserContext);
  const [lessons, setLessons ] = useState([]);
  // console.log(`lessons.length: ${lessons.length}`);
  // console.log(lessons);
  const [activeLessonId, setActiveLessonId] = useState(
    (!!lessonParam && lessons.length !== 0) ? lessons.find(l => l.lesson_position === parseInt(lessonParam)).id
  : null);
  // console.log(`activeLessonId: ${activeLessonId}`);
  const [dimensions, setDimensions] = useState({
      height: window.innerHeight,
      width: window.innerWidth
  });
  const [loaded, setLoaded] = useState(false);

  const activeLessonSrc = !!activeLessonId ?
    lessons.find(l => l.id===activeLessonId).video_url.replace("https://youtu.be/", "https://www.youtube.com/embed/")
  : null ;

  const [defaultSet, setDefaultSet ] = useState(!!lessonParam ? parseInt(lessonParam.slice(0, -1)) : user.currentBadgeSet);

  // Refresh video when param changes even if already on video page
  useEffect(() => {
    setLoaded(false);
    setActiveLessonId(
      (!!lessonParam && lessons.length !== 0) ? lessons.find(l => l.lesson_position === parseInt(lessonParam)).id
      : null
    );
  }, [lessonParam, lessons]);

  useEffect( () => {
    fetchLessons()
    .then(mydata => {
      setLessons(mydata);
      setActiveLessonId(!!lessonParam ?
        mydata.find(l => l.lesson_position===parseInt(lessonParam)).id : null
      );
      setLoaded(true);
    });
  }, [lessonParam]);

  useEffect( () => {
    if (!!loaded) {
      // console.log("video loaded!");
      // let $mask = document.getElementsByClassName("iframe-mask")[0];
      window.setTimeout(() => {
        let $mask = document.getElementsByClassName("iframe-mask")[0];
        // console.log($mask);
        $mask.classList.add("iframe-loaded");
        window.setTimeout(() => $mask.classList.add("mask-done"), 200);
      }, 1500);
    }
  }, [loaded])

  useLayoutEffect( () => {
    const setListHeight = () => {

      // console.log(`width: ${window.innerWidth}`);
      let $videoFrame = document.getElementsByClassName("embed-responsive")[0];
      let videoHeight = $videoFrame.offsetHeight;
      // console.log(`videoHeight: ${videoHeight}`);
      let $listContainer = document.getElementsByClassName("lessonlist")[0];
      let $lessonsContainer = document.getElementsByClassName("lessons-display-container")[0];
      let containerHeight = $lessonsContainer.offsetHeight;
      // console.log(`containerHeight: ${containerHeight}`);
      let remainingHeight = containerHeight - videoHeight;
      if (window.innerWidth >= 768) {
        remainingHeight = containerHeight;
      }
      // console.log(`remainingHeight: ${remainingHeight}`);
      $listContainer.style.height = `${remainingHeight}px`;
    };
    window.addEventListener('resize', setListHeight);

    return _ => {
      window.removeEventListener('resize', setListHeight);
    }
  }, [dimensions]);

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
            { lessons.length !== 0 &&
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
              unmountOnExit={true}
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
                unmountOnExit={true}
              >
                  <div className="youtube-container">
                    <div className="iframe-mask">
                      <Spinner animation="grow" variant="secondary" />
                    </div>
                    <ResponsiveEmbed aspectRatio="16by9">
                      <iframe
                        title={`lesson display: lesson ${activeLessonId}`}
                        src={activeLessonSrc}
                        frameBorder="0"
                        onLoad={() => setLoaded(true)}
                        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowFullScreen
                      >
                      </iframe>
                    </ResponsiveEmbed>
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
