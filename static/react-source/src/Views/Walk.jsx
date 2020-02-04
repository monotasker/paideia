import React, { useState, useContext } from "react";
import { Row, Spinner } from "react-bootstrap";
import { CSSTransition } from "react-transition-group";
import { withRouter } from "react-router";

import SvgMap from "./SvgMap";
import Step from "./Step";
import { getPromptData } from "../Services/stepFetchService";
import { UserContext } from "../UserContext/UserProvider";
import { returnStatusCheck } from "../Services/authService";


const Walk = (props) => {
    const { user, dispatch } = useContext(UserContext);
    const [ currentPage, setCurrentPage ] = useState(props.location.search || "map");
    const [mapIn, setMapIn] = useState(true);
    const [stepIn, setStepIn] = useState(false);
    const [stepData, setStepData] = useState(false);

    const goToLocation = async (newLoc) => {
      setCurrentPage(newLoc);
      if ( newLoc != "map" ) {
        getPromptData({location: newLoc})
        .then(stepfetch => {
          returnStatusCheck(stepfetch, props.history,
            (myfetch) => {
              myfetch.json().then((mydata) => {
                setStepData(mydata);
                setStepIn(true);
                setMapIn(false);
              });
            },
            dispatch
          )
        });
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
          unmountOnExit={true}
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
