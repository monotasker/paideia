import React from "react";
import {
    Row,
    Col,
    Button
} from "react-bootstrap";

const Step = (props) => {

  return (
    <Row id="step_row" className="stepPane" >
      <Col>
      </Col>
      <Col>
        <Row>
          <div>
            {props.stepdata.prompt_text}
          </div>
        </Row>
        <Row>
          <Button
            onClick={() => props.navfunction("map")}
            >
            Click me
          </Button>
        </Row>
      </Col>
    </Row>
  )
}

export default Step;
