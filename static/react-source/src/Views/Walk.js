import React, { useState, useContext } from "react";
import { Row } from "react-bootstrap";
import { CSSTransition } from "react-transition-group";
import { withRouter } from "react-router";

import SvgMap from "./SvgMap.js";
import Step from "./Step.js";
import { getPromptData, evaluateAnswer } from "../Services/stepFetchService";
import { UserContext } from "../UserContext/UserProvider";


const Walk = (props) => {
    const { user, dispatch } = useContext(UserContext);
    const [ currentPage, setCurrentPage ] = useState(props.location.search || "map");
    const [mapIn, setMapIn] = useState(true);
    const [stepIn, setStepIn] = useState(false);
    const [stepData, setStepData] = useState(false);
    let history = props.history;
 
    const goToLocation = async (newLoc) => {
      setCurrentPage(newLoc);
      setMapIn(newLoc == "map" ? true : false);
      setStepIn(newLoc == "map" ? false : true);
      if ( newLoc != "map" ) {
        let stepData = await getPromptData({location: newLoc});        
        console.log("status is " + stepData.status);
        if ( stepData.status == 'okay' ) {
          setStepData(stepData);
          setStepIn(true);
          console.log('stepIn is ' + stepIn);
          setMapIn(false);
        } else if ( stepData.status == 'unauthorized' ) {
          dispatch({type: 'deactivateUser', payload: null});
          history.push("/login");
        }
        console.log(stepData);
      }
    }

    return (
      <Row className="walk-container" >
        <CSSTransition
          in={ mapIn }
          classNames="svgMapPane"
          timeout={{
            appear: 2000,
            enter: 0,
            exit: 0
          }}
          appear={true}
          unmountOnExit={false}
        >
          <SvgMap
            navFunction={goToLocation}
            id="town_map"
          />
        </CSSTransition>

        <CSSTransition
          in={ stepIn }
          classNames="stepPane"
          timeout={0}
          appear={true}
        >
          <Step
            myroute={currentPage}
            navfunction={goToLocation}
            stepdata={stepData}
          />
        </CSSTransition>

      </Row>
    )
}

export default withRouter(Walk);
