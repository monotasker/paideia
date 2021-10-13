import React, { useState, useContext, useEffect } from "react";
import { Row, Spinner } from "react-bootstrap";
import { CSSTransition } from "react-transition-group";
import { useParams,
         useHistory
} from "react-router-dom";

import SvgMap from "./SvgMap";
import Step from "./Step";
import { getPromptData } from "../Services/stepFetchService";
import { UserContext } from "../UserContext/UserProvider";
import { returnStatusCheck } from "../Services/utilityService";
import { urlBase } from "../variables";


const Walk = () => {
    const { walkPage, walkStep } = useParams();
    // console.log("walkPage");
    // console.log(walkPage);
    const history = useHistory();

    const { user, dispatch } = useContext(UserContext);
    const [ currentPage, setCurrentPage ] = useState(walkPage || "map");
    const [stepData, setStepData] = useState(false);
    // console.log("STEPDATA IS");
    // console.log(stepData);

    useEffect(() => {
      if ( currentPage != "map" ) {
        // console.log("###############");
        // console.log("setting step on Walk refresh");
        const myStep = !!walkStep ? walkStep : null;
        getPromptData({location: walkPage, repeat: false, step: myStep})
        .then(stepfetch => {
          returnStatusCheck(stepfetch, history,
            (mydata) => {
                setStepData(mydata);
            },
            dispatch
          )
        });
      }
    }, []);

    const goToLocation = async ({newLoc=null, retrying=false}) => {
      setCurrentPage(newLoc);
      if ( newLoc != "map" ) {
        getPromptData({location: newLoc, repeat: retrying})
        .then(stepfetch => {
          returnStatusCheck(stepfetch, history,
            (mydata) => {
                setStepData(mydata);
                history.push(`/${urlBase}/walk/${newLoc}/${mydata.sid}`)
            },
            dispatch
          )
        });
      }
    };

    return (
      <Row className="walk-container" >
        <CSSTransition
          in={ walkPage=="map" }
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
          in={ walkPage!="map" }
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

export default Walk;
