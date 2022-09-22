import React, { useEffect, useState, useContext } from "react";
import {
    Row,
    Col,
    Button,
    Form,
    OverlayTrigger,
    Tooltip,
    Badge,
    ButtonGroup
} from "react-bootstrap";
import Popover from "react-bootstrap/Popover";
import { useHistory, Link } from "react-router-dom";
import { CSSTransition } from "react-transition-group";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle } from '@fortawesome/free-solid-svg-icons';
import { marked } from "marked";
import DOMPurify from 'dompurify';
import TextareaAutosize from 'react-textarea-autosize';

import { urlBase, DEBUGGING } from "../variables";
import AudioPlayer from "../Components/AudioPlayer";
import { evaluateAnswer, set_lessons_viewed, getPromptData } from "../Services/stepFetchService";
import { UserContext } from "../UserContext/UserProvider";
import useEventListener from "../Hooks/UseEventListener";
import { returnStatusCheck } from "../Services/utilityService";

const Instructions = ({instructions}) => {

  const inst_set = {
    "Please answer in Greek.": ["font", "Γ"],
    "Please answer in English.": ["icon", "font"],
    "Please answer with a complete Greek clause.": ["icon", "arrows-alt-h"],
    "Choose one of the options listed.": ["icon", "check-circle"]
  }
  const instructions_extra = [
    "Remember to vary the word order in your Greek clauses"]

  const icons = instructions.map( inst =>
    Object.keys(inst_set).includes(inst) ?
      (
        <OverlayTrigger key={inst} placement="top"
          overlay={<Tooltip id={`tooltip-instruction-${inst}`}>{inst}</Tooltip>}
          trigger={['click', 'focus', 'hover']}
        >
            { inst_set[inst][0] === "font" ? (
              <a className='instruction-icon text-icon'>{inst_set[inst][1]}</a>
              ) : (
              <a className='instruction-icon'><FontAwesomeIcon key="1" icon={inst_set[inst][1]} /></a>
              )
            }
        </OverlayTrigger>
      )
      : ""
  );

  const extra_strs = instructions.filter( inst => {
    return !Object.keys(inst_set).includes(inst);
  });

  if ( extra_strs.length > 0 ) {
    const extra = extra_strs.map( inst => <li key={inst} ><FontAwesomeIcon key="1" icon="info-circle" size="sm" />{inst}</li> );
    const extra_icon = (
      <OverlayTrigger key="extra-instruction-trigger" placement="top"
        overlay={<Tooltip id="tooltip-instruction-extra"><ul>{extra}</ul></Tooltip>}
        trigger={['click', 'hover', 'focus']}
      >
        <a className='instruction-icon'>
          <FontAwesomeIcon key="1" icon="info-circle" />
        </a>
      </OverlayTrigger>
    );
    icons.push(extra_icon);
  }
  return icons;
}

const Slidedecks = ({decks}) => {
  return(
    <OverlayTrigger placement="top" trigger="click" rootClose
      overlay={
        <Popover id="lessons-tooltip" >
          <Popover.Header>Related lessons</Popover.Header>
          <Popover.Body>
            <ul>
              {Object.entries(decks).map(([id, label]) =>
                <li key={label}>
                  <FontAwesomeIcon icon="video" size="sm" />
                  <Link to={`/${urlBase}/videos/${id}`}>
                    {label}
                  </Link>
                </li>
              )}
            </ul>
          </Popover.Body>
        </Popover>
    }>
      <a className='instruction-icon lessons-icon'>
        <FontAwesomeIcon  icon="video" />
      </a>
    </OverlayTrigger>
  )
}

const Step = (props) => {
  DEBUGGING && console.log(props);
  const history = useHistory();
  const { user, dispatch } = useContext(UserContext);
  const [ stepData, setStepData ] = useState(props.stepdata);
  const [ evalText, setEvalText ] = useState(null);
  const [ promptText, setPromptText] = useState(stepData.prompt_text);
  const [ score, setScore ] = useState(null);
  const [ answer, setAnswer ] = useState(null);
  const [ logID, setLogID ] = useState(null);
  const [ promptZIndex, setPromptZIndex ] = useState(null);
  const [ respButtons, setRespButtons ] = useState(stepData.response_buttons);
  const [ evaluatingStep, setEvaluatingStep ] = useState(false);
  const [ responded, setResponded ] = useState(false);
  DEBUGGING && console.log('STEPDATA IS (in Step)');
  DEBUGGING && console.log(stepData);
  DEBUGGING && console.log(stepData.audio);

  useEffect(() => {
    setStepData(props.stepdata);
    setPromptText(props.stepdata.prompt_text);
    setRespButtons(props.stepdata.response_buttons);
  }, [props.stepdata]);

  useEffect(() => {
    dispatch({type: 'setCurrentLoc', payload: props.myroute});
  }, []);

  useEffect(() => {
    dispatch({type: 'setCurrentStep',
              payload: {step: stepData.sid, path: stepData.pid}});
  }, [stepData.sid, stepData.pid, dispatch]);

  useEffect(() => {
    dispatch({type: 'setEvalResults',
              payload: {answer: answer,
                        score: score,
                        logId: logID}
            });
  }, [evalText]);

  useEffect(() => {
    let $eval = document.querySelector('.eval-text');
    let $p = document.querySelector('.prompt-text');
    $eval && ($eval.style.marginTop = `${-1 * ($p.offsetHeight - 24)}px`);
  });

  useEventListener("cut copy paste",
    (event) => {event.preventDefault()},
    document.querySelector('.responder textarea')
  );

  useEventListener("click",
    () => {
      set_lessons_viewed();
      setPromptText(null);
    },
    document.querySelector('.new-lessons-dismiss'));

  useEventListener("click mouseover", setPromptZIndex,
    document.querySelector('.prompt-text'));

  const submitAction = (event) => {
    event.preventDefault();
    setEvaluatingStep(true);
    let $myform = event.target;
    let myval = null;
    if ( !!$myform.querySelector("#responder_field") ) {
      myval = $myform.querySelector("#responder_field").value;
    } else {
      myval = $myform.querySelectorAll("input[name=responder_radio]:checked")[0].value;
    }
    evaluateAnswer({location: props.stepdata.loc,
                    response_string: myval,
                    pre_bug_step_id: stepData.sid})
      .then(stepfetch => {
        returnStatusCheck(stepfetch, history,
          (mydata) => {
              DEBUGGING && console.log(mydata);
              setEvaluatingStep(false);
              setResponded(true);
              setScore(mydata.score);
              setLogID(mydata.bugreporter.log_id);
              setAnswer(mydata.user_response);
              setRespButtons(mydata.response_buttons);
              setEvalText(mydata.eval_text);
          },
          dispatch)
      });
  }

  const mapAction = () => {
    setResponded(false);
    setEvalText(null);
    setPromptText("");
    setRespButtons(null);
    history.push(`/${urlBase}/walk/map`);
    // props.navfunction({newLoc: "map"});
  }

  const retryAction = () => {
    setResponded(false);
    setPromptText("");
    setEvalText(null);
    setRespButtons(null);
    getPromptData({location: props.myroute, repeat: true})
    .then(stepfetch => {
      returnStatusCheck(stepfetch, history,
        (mydata) => {
            setStepData(mydata);
            setPromptText(mydata.prompt_text);
            setRespButtons(mydata.response_buttons);
        },
        dispatch)
    });
  }

  const continueAction = () => {
    setResponded(false);
    setPromptText(null);
    setEvalText(null);
    getPromptData({location: props.myroute})
    .then(stepfetch => {
      returnStatusCheck(stepfetch, history,
        (mydata) => {
            setStepData(mydata);
            setPromptText(mydata.prompt_text);
            setRespButtons(mydata.response_buttons);
            history.push(`/${urlBase}/walk/${props.myroute}/${mydata.sid}`);
        },
        dispatch)
    });
  }



  const widgets = {
    'text': () => <Form.Control autoFocus type="text" name="responder_field"
      id="responder_field" as={TextareaAutosize} />,
    'radio': () => {if (stepData.response_form.values != null) {
        return stepData.response_form.values.map( val => (
          <Form.Check
            autoFocus
            type="radio"
            name={`responder_radio`}
            id={`radio-${val}`}
            key={`radio-${val}`}
            label={val}
            value={val}
          />
        ))
      }
    }
  }

  const response_btns = {
    'map': () => (<Button className="back_to_map"
                    autoFocus
                    key="back_to_map"
                    onClick={mapAction}>
                    <FontAwesomeIcon icon="map" />
                      <span className="short-label">Map</span>
                      <span className="long-label">Back to map</span>
                  </Button>),
    'retry': () => (<Button className="retry" variant="warning"
                      key="retry"
                      onClick={retryAction}>
                      <FontAwesomeIcon icon="redo-alt" /> Retry
                    </Button>),
    'continue': () => (<Button className="continue" variant="success"
                        autoFocus
                        key="continue"
                        onClick={continueAction}>
                        <FontAwesomeIcon icon="walking" />
                          <span className="short-label">Continue</span>
                          <span className="long-label">Continue here</span>
                       </Button>)
  }



  return (
    <Row id="step_row" className="stepPane"
      style={{backgroundImage: `url("${stepData.bg_image}")`}}
    >
        <div className="speaker-inner-wrapper">
          <img src={stepData.npc_image}
            alt="The current speaker addressing the student"
          />
        </div>
      <Col className="speaker" sm={4} xs={12}>
      </Col>
      <Col sm={8} xs={12} className="prompt-column">
        <Row className="npc prompt">
          <CSSTransition
            in={ !!promptText }
            classNames="prompt-text"
            timeout={0}
            appear={true}
          >
            <div className="prompt-text" style={{zIndex: promptZIndex}}>
              <p dangerouslySetInnerHTML={{
                __html: !!promptText ? DOMPurify.sanitize(marked(promptText)) : ""
              }} />
              { !!stepData.widget_img && (
                <img
                  className="prompt-image"
                  src={`/paideia/static/images/${stepData.widget_img.file}`}
                  alt={stepData.widget_img.description}
                />
              )}
              { stepData.audio != null &&
                <AudioPlayer
                  m4aSource={`${stepData.download_path}/${stepData.audio.m4a}`}
                  mp3Source={`${stepData.download_path}/${stepData.audio.mp3}`}
                  ogaSource={`${stepData.download_path}/${stepData.audio.oga}`}
                />
              }
            </div>
          </CSSTransition>
          <CSSTransition
              in={ !!evalText }
              classNames="eval-text"
              timeout={0}
              appear={true}
            >
            <div className="eval-text">
              <p dangerouslySetInnerHTML={{
                  __html: !!evalText ? DOMPurify.sanitize(marked(evalText)) : "" }}
              />
            </div>
          </CSSTransition>
        </Row>
        <Row className="responder">
          <Col >
            <div className="responder-text">
          { !!stepData.response_form && !responded && (
            <Form onSubmit={submitAction}>
              <div className="instruction-row">
                { !!stepData.instructions &&
                  <Instructions instructions={stepData.instructions} />
                }
                { !!stepData.slidedecks &&
                  <Slidedecks decks={stepData.slidedecks} />
                }
              </div>
              {widgets[stepData.response_form.form_type]()}
              <Button variant="success" type="submit" className="submit_reply">
                { evaluatingStep ? (
                    <FontAwesomeIcon icon="spinner" pulse />
                  ) : ( "Submit Reply" )
                }
              </Button>
            </Form>
          )}
            { !!respButtons && respButtons.length > 0 && (
            <ButtonGroup className="responder-btn-group">
              {respButtons.map(btn => response_btns[btn]())}
            </ButtonGroup>
            )
            }
            { user.userRoles.includes('administrators') && (
              <div className="admin-info">
                <span className="step-id">step {stepData['sid']},</span>&nbsp;
                <span className="path-id">path {stepData['pid']},</span>&nbsp;
                <span className="selection-level"> chosen from selection level {stepData.category}</span>&nbsp;
              </div>
            )}
              <div className="user-info">
                {!!user.reviewSet &&
                  <Badge className="review-warning" variant="warning">
                    <FontAwesomeIcon icon="history" />
                    Reviewing just badge set {user.reviewSet}
                  </Badge>
                }
                <span className="current-count">
                  {!responded ? `This will make` : `You have finished`}
                  {` ${stepData.completed_count + 1} path`}
                  {stepData.completed_count + 1 > 1 && "s"}
                  {" today"}
                </span>
              </div>
              <span className="new-indicator">
                {stepData.new_content ? <FontAwesomeIcon icon="leaf" /> : <FontAwesomeIcon icon="history" />}
              </span>
            </div>
          </Col>
        </Row>
      </Col>
    </Row>
  )
}

export default Step;
