import React, { useEffect, useState, useContext } from "react";
import {
    Row,
    Col,
    Button,
    Form,
    OverlayTrigger,
    Tooltip
} from "react-bootstrap";
import { withRouter } from "react-router";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import marked from "marked";
import DOMPurify from 'dompurify';

import AudioPlayer from "../Components/AudioPlayer";
import { evaluateAnswer } from "../Services/stepFetchService";
import { UserContext } from "../UserContext/UserProvider";
import useEventListener from "../Hooks/UseEventListener";


const Step = (props) => {
  console.log(props);
  const { user, dispatch } = useContext(UserContext);
  const [ evalText, setEvalText ] = useState(null);
  const [ promptZIndex, setPromptZIndex ] = useState(null);
  const [ respButtons, setRespButtons ] = useState(props.stepdata.response_buttons);
  const [ evaluatingStep, setEvaluatingStep ] = useState(false);
  const [ responded, setResponded ] = useState(false);

  useEffect(() => {
    let $eval = document.querySelector('.eval-text');
    let $p = document.querySelector('.prompt-text');
    $eval && ($eval.style.marginTop = `${-1 * ($p.offsetHeight - 24)}px`);
  });
  useEventListener("cut copy paste",
    (event) => {event.preventDefault()},
    document.querySelector('.responder input')
  );
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
                    response_string: myval})
      .then((stepfetch) => {
        if ( stepfetch.status === 200 ) {
          stepfetch.json().then((mydata) => {
            console.log(mydata);
            ;
            setEvaluatingStep(false);
            setResponded(true);
            setEvalText(mydata.eval_text);
            setRespButtons(mydata.response_buttons);
          })
        } else if ( stepfetch.status === 401 ) {
          dispatch({type: 'deactivateUser', payload: null});
          history.push("/login");
        }
      });
    event.preventDefault();
  }

  const widgets = {
    'text': () => <Form.Control type="text" name="responder_field" id="responder_field" />,
    'radio': () => {if (props.stepdata.response_form.values != null) {
        return props.stepdata.response_form.values.map( val => (
          <Form.Check 
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
                    key="back_to_map"
                    onClick={() => props.navfunction("map")}>
                    <FontAwesomeIcon icon="map" /> Back to map
                  </Button>),
    'retry': () => (<Button className="retry"
                      key="retry"
                      onClick={() => props.navfunction("map")}>
                      <FontAwesomeIcon icon="redo-alt" /> Retry
                    </Button>),
    'continue': () => (<Button className="continue"
                        key="continue"
                        onClick={() => props.navfunction(props.myroute) && setResponded(false)}>
                        <FontAwesomeIcon icon="walking" /> Continue here
                       </Button>)
  }

  const inst_set = {
    "Please answer in Greek.": ["font", "Γ"],
    "Please answer in English.": ["icon", "font"],
    "Please answer with a complete Greek clause.": ["icon", "arrows-alt-h"], 
  }
  const instructions_extra = [
    "Remember to vary the word order in your Greek clauses"]

  const make_instructions = () => {
    const icons = props.stepdata.instructions.map( inst => {
      if ( Object.keys(inst_set).includes(inst) ) {
        return(
          <OverlayTrigger key={inst} placement="top"
            overlay={<Tooltip id={`tooltip-${inst}`}>{inst}</Tooltip>}
          >
              { inst_set[inst][0] === "font" ? (
                <a className='instruction-icon text-icon'>{inst_set[inst][1]}</a> 
                ) : (
                <a className='instruction-icon'><FontAwesomeIcon key="1" icon={inst_set[inst][1]} /></a>
                )
              }
          </OverlayTrigger>
        )} 
    });
    const extra_strs = props.stepdata.instructions.filter( inst => {
      return !Object.keys(inst_set).includes(inst); 
    });
    console.log(extra_strs);
    if ( extra_strs.length > 0 ) {
      const extra = extra_strs.map( inst => <li key={inst} >{inst}</li> );
      const extra_icon = (
        <OverlayTrigger key="extra-instruction-trigger" placement="top"
          overlay={<Tooltip id="tooltip-extra"><ul>{extra}</ul></Tooltip>}
        >
          <a className='instruction-icon'>
            <FontAwesomeIcon key="1" icon="info-circle" />
          </a>
        </OverlayTrigger>
      );
      icons.push(extra_icon);
    }
    console.log(icons);
    return icons;    
  }

  return (
    <Row id="step_row" className="stepPane" 
      style={{backgroundImage: `url("${props.stepdata.bg_image}")`}}
    >
      <Col className="speaker" sm={4} xs={12}>
        <img src={props.stepdata.npc_image} 
          alt="The current speaker addressing the student"
        />
      </Col>
      <Col sm={8} xs={12}>
        <Row className="npc prompt">
          <div className="prompt-text" style={{zIndex: promptZIndex}}>
            <p dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(marked(props.stepdata.prompt_text))
            }} />
            { !!props.stepdata.widget_img && (
              <img
                className="prompt-image"
                src={`/paideia/static/images/${props.stepdata.widget_img.file}`}
                alt={props.stepdata.widget_img.description}
              />
            )}
            <AudioPlayer
              mp3Source="http://techslides.com/demos/samples/sample.mp3" 
              oggSource="http://techslides.com/demos/samples/sample.ogg"
            />
          </div>
          { !!evalText && (
            <div className="eval-text">
              <p dangerouslySetInnerHTML={{
                __html: DOMPurify.sanitize(marked(evalText))
              }} />
            </div>
          )}
        </Row>
        <Row className="responder">
          <Col >
            <div className="responder-text">
          { !!props.stepdata.response_form && !responded && (
            <Form onSubmit={submitAction}>
              { !!props.stepdata.instructions && make_instructions()}
              {widgets[props.stepdata.response_form.form_type]()}
              <Button variant="success" type="submit">
                { evaluatingStep ? (
                    <FontAwesomeIcon icon="spinner" pulse /> 
                  ) : ( "Submit Reply" )
                }
              </Button>
            </Form>
          )}
          { respButtons.length > 0 && respButtons.map(btn => response_btns[btn]()) }
            </div>
          </Col>
        </Row>
      </Col>
    </Row>
  )
}

export default withRouter(Step);
