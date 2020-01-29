import React, { useState, useContext } from "react";
import { Row, Spinner } from "react-bootstrap";
import { CSSTransition } from "react-transition-group";
import { withRouter } from "react-router";

import SvgMap from "./SvgMap";
import Step from "./Step";
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
      if ( newLoc != "map" ) {
        let stepfetch = getPromptData({location: newLoc})
          .then((stepfetch) => {
            if ( stepfetch.status === 200 ) {
              stepfetch.json().then((mydata) => {
                setStepData(mydata);
                setStepIn(true);
                setMapIn(false);
              });
            } else if ( stepfetch.status === 401 ) {
              dispatch({type: 'deactivateUser', payload: null});
              history.push("/login");
            }
          }
          );        
      } else {
        setStepIn(false);
        setMapIn(true);
      }
    };

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
          mountOnEnter={true}
        >
          <Step
            myroute={currentPage}
            navfunction={goToLocation}
            stepdata={stepData}
          />
        </CSSTransition>
        <Spinner animation="grow" variant="secondary" className="align-self-center map-spinner" />
      </Row>
    )
}

export default withRouter(Walk);
