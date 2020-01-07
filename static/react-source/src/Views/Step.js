import React from "react";
import {
    Row,
    Col,
    Button
} from "react-bootstrap";

const Step = (props) => {

  return (
    <Row id="step_row" className="stepPane" >
      <div>
        {props.myroute}
        <Button
          onClick={() => props.navfunction("map")}
          >
          Click me
        </Button>
      </div>
      <div>
        {props.stepdata.prompt}
      </div>
    </Row>
  )
}

export default Step;
