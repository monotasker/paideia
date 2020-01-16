import React, { useEffect } from "react";
import {
    Row,
    Col,
    Button,
    Form
} from "react-bootstrap";

import AudioPlayer from "../Components/AudioPlayer";

const Step = (props) => {
  console.log(props);

  useEffect(() => {
    let $input = document.querySelector('.responder input');
    if ( $input ) {
      $input.addEventListener("cut copy paste", (event) => {
          event.preventDefault();
      });
    }
  });

  const submitAction = () => {
    console.log('fired!');
  }

  const widgets = {
    'text': () => <Form.Control type="text" name="responder_field" />,
    'radio': () => {props.stepdata.response_form.values != null && (
      <React.Fragment>
        {props.stepdata.response_form.values.map( val => (
          <Form.Check 
            type="radio"
            id={`radio-${val}`}
            label={val}
            value={val}
          />
        ))}
      </React.Fragment>
    )}
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
          <p className="prompt-text">
            {props.stepdata.prompt_text}
            <AudioPlayer mp3Source="http://techslides.com/demos/samples/sample.mp3" oggSource="http://techslides.com/demos/samples/sample.ogg" />
          </p>
        </Row>
        <Row className="responder">
          { props.stepdata.response_form != null && (
            <Form onSubmit={submitAction}>
              {widgets[props.stepdata.response_form.form_type]()}
              <Button variant="success" type="submit">Submit Reply</Button>
            </Form>
          )
          }
          <Button
            className="back_to_map"
            onClick={() => props.navfunction("map")}
            >
            Back to map
          </Button>
        </Row>
      </Col>
    </Row>
  )
}

export default Step;
