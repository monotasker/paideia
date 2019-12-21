import React, { useState, useContext } from "react";
import ReactDOM from "react-dom";
import { Container } from "react-bootstrap";
// import { LinkContainer } from "react-router-bootstrap";
import { CSSTransition } from "react-transition-group";
import styled from "styled-components";
// import Velocity from "velocity-animate";
import { withRouter } from "react-router";

// import { make_map_pan } from "../Services/mapNavService";
import SvgMap from "./SvgMap.js";
import Step from "./Step.js";

const WalkRow = styled.div`

  .svgMapPane-enter,
  .svgMapPane-appear {
    opacity: 0;
  }

  .svgMapPane-enter-done,
  .svgMapPane-appear-done {
    opacity: 1;
    transition: opacity 1000ms;
  }

  .svgMapPane-exit {
    opacity: 1;
  }

  .svgMapPane-exit-active {
    opacity: 0;
    transition: opacity 500ms;
  }

  .svgMapPane-exit-done {
    opacity: 0;
    display: none;
  }

  .stepPane-enter {
    opacity: 0;
  }

  .stepPane-enter-done {
    opacity: 1;
    transition: opacity 300ms;
  }

  .stepPane-exit {
    opacity: 1;
  }

  .stepPane-exit-active {
    opacity: 0;
    transition: opacity 300ms;
  }

  .stepPane-exit-done {
    opacity: 0;
    position: absolute;
  }
`;

const Walk = (props) => {
    console.log(props);
    let activeRoutes = ["path5424", "path5418"];

    const [ currentPage, setCurrentPage ] = useState(props.location.search || "map");
    const [mapIn, setMapIn] = useState(true);
    const [stepIn, setStepIn] = useState(false);
 
    const goToLocation = (newLoc) => {
      setCurrentPage(newLoc);
      setMapIn(newLoc == "map" ? true : false);
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
      <WalkRow className="walk-container" >
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

      </WalkRow>
    )
}



export default withRouter(Walk);
