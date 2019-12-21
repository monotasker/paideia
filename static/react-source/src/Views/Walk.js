import React, { useState, useContext } from "react";
import { Row } from "react-bootstrap";
import { CSSTransition } from "react-transition-group";
import { withRouter } from "react-router";

import SvgMap from "./SvgMap.js";
import Step from "./Step.js";
import { getPromptData, evaluateAnswer } from "../Services/stepFetchService";


const Walk = (props) => {
    console.log(props);

    const [ currentPage, setCurrentPage ] = useState(props.location.search || "map");
    const [mapIn, setMapIn] = useState(true);
    const [stepIn, setStepIn] = useState(false);
 
    const goToLocation = (newLoc) => {
      setCurrentPage(newLoc);
      setMapIn(newLoc == "map" ? true : false);
      if ( newLoc != "map" ) {
        let stepData = getPromptData(newLoc);        
        console.log(stepData);
      }
    }

    const evaluateStep = () => {
    }

    const showStep = () => {
      console.log("fired showStep!");
      setStepIn(true);
    }

    const showMap = () => {
      console.log("fired showMap!");
      setMapIn(true);
    }

    return (
      <Row className="walk-container" >
        <CSSTransition
          in={ mapIn }
          classNames="svgMapPane"
          timeout={2000}
          appear={true}
          onExited={showStep}
        >
          <SvgMap
            navFunction={goToLocation}
            id="town_map"
          />
        </CSSTransition>

        <CSSTransition
          in={ stepIn }
          classNames="stepPane"
          timeout={300}
          onExited={showMap}
          mountOnEnter
        >
          <Step
            myroute={currentPage}
            navfunction={goToLocation}
          />
        </CSSTransition>

      </Row>
    )
}

export default withRouter(Walk);
