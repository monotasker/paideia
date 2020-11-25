import React, { useEffect, useState, useContext } from 'react';
import {
  Row,
  Col,
} from "react-bootstrap";
import {
  Switch,
  Route,
  BrowserRouter,
  useLocation
} from "react-router-dom";
import { CSSTransition } from "react-transition-group";
import { library } from '@fortawesome/fontawesome-svg-core';
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faArrowsAltH,
  faBalanceScale,
  faBolt,
  faBug,
  faCaretDown,
  faCertificate,
  faChalkboardTeacher,
  faCheckCircle,
  faChevronLeft,
  faChevronRight,
  faClock,
  faCog,
  faComment,
  faEnvelope,
  faExclamationTriangle,
  faEye,
  faEyeSlash,
  faFilter,
  faFlag,
  faFont,
  faGlobeAmericas,
  faHardHat,
  faHistory,
  faHome,
  faInfoCircle,
  faKeyboard,
  faLeaf,
  faLightbulb,
  faQuestionCircle,
  faRedoAlt,
  faMap,
  faPencilAlt,
  faPlus,
  faReply,
  faSearch,
  faSeedling,
  faSignInAlt,
  faSignOutAlt,
  faSlidersH,
  faSort,
  faSortUp,
  faSortDown,
  faSortAlphaDown,
  faSpinner,
  faThumbsUp,
  faThumbtack,
  faTimesCircle,
  faTrashAlt,
  faUser,
  faUserCircle,
  faUsers,
  faVideo,
  faWalking,
  faWrench,
} from '@fortawesome/free-solid-svg-icons';

import './Main.scss';

import { urlBase } from "../variables";
import PrivateRoute from "../Components/PrivateRoute";
import TopNavbar from "../Components/TopNavbar";
import Tools from "../Components/Tools";
import Home from "./Home";
import Login from "./Login";
import Walk from "./Walk";
import Profile from "./Profile";
import Videos from "./Videos";
import Info from "./Info";
import Admin from "./Admin";
import Instructors from "./Instructors";
import UserProvider, { UserContext } from "../UserContext/UserProvider";
import { checkLogin } from '../Services/authService';

library.add(
  faArrowsAltH,
  faBalanceScale,
  faBolt,
  faBug,
  faCaretDown,
  faCertificate,
  faChalkboardTeacher,
  faCheckCircle,
  faChevronLeft,
  faChevronRight,
  faClock,
  faCog,
  faComment,
  faEnvelope,
  faExclamationTriangle,
  faEye,
  faEyeSlash,
  faFilter,
  faFlag,
  faFont,
  faGlobeAmericas,
  faHardHat,
  faHistory,
  faHome,
  faInfoCircle,
  faKeyboard,
  faLeaf,
  faLightbulb,
  faPencilAlt,
  faPlus,
  faQuestionCircle,
  faRedoAlt,
  faMap,
  faReply,
  faSearch,
  faSeedling,
  faSignInAlt,
  faSignOutAlt,
  faSlidersH,
  faSort,
  faSortAlphaDown,
  faSortUp,
  faSortDown,
  faSpinner,
  faTrashAlt,
  faThumbsUp,
  faThumbtack,
  faTimesCircle,
  faUser,
  faUserCircle,
  faUsers,
  faVideo,
  faWalking,
  faWrench,
);


const myroutes = [
  {path: "/" + urlBase + "(/static/react-source/dist/index.html||/home)", exact: true, Component: Home},
  {path: "/" + urlBase + "/videos/:lessonParam?", exact: false, Component: Videos},
  {path: "/" + urlBase + "/info/:infoPage", exact: false, Component: Info},
  {path: "/" + urlBase + "/login", exact: false, Component: Login}
]

const myPrivateRoutes = [
  {path: "/" + urlBase + "/walk/:walkPage/:walkStep?", exact: false, Component: Walk},
  {path: "/" + urlBase + "/profile", exact: false, Component: Profile},
  {path: "/" + urlBase + "/admin/:adminPage", exact: false, Component: Admin},
  {path: "/" + urlBase + "/instructors/:instrPage", exact: false, Component: Instructors},
]

const MainPage = () => {
  const [ myheight, setMyheight ] = useState(null);
  const { user, dispatch } = useContext(UserContext);

  const setHeight = () => {
    const headroom = document.querySelector('.navbar').offsetHeight;
    let divheight = window.innerHeight - headroom;
    setMyheight(divheight);
  }

  useEffect(() => {
    setHeight();
  });

  useEffect(() => {
    console.log('=================================');
    console.log('Checking login in Main');
    checkLogin(user, dispatch);
  }, []);

  return (
    <Col className="content"
      style={{height: myheight}}
    >
      <Switch>
      {myPrivateRoutes.map(({ path, exact, Component }) => (
        <PrivateRoute key={path} exact={exact} path={path} >
          {( { match } ) => (
          <CSSTransition
            classNames="content-view"
            key={path}
            in={match != null}
            appear={true}
            timeout={300}
            unmountOnExit
          >
            <React.Fragment>
              <Component />
              <Tools />
            </React.Fragment>
          </CSSTransition>
          )}
        </PrivateRoute>
      )
      )}
      {myroutes.map(({ path, exact, Component }) => (
        <Route key={path} exact={exact} path={path}>
          {( { match } ) => (
            <CSSTransition
              classNames="content-view"
              key={path}
              in={match != null}
              appear={true}
              timeout={300}
              unmountOnExit
            >
              <React.Fragment>
                <Component />
                <Tools />
              </React.Fragment>
            </CSSTransition>
          )}
        </Route>
      )
      )}
      </Switch>
    </Col>
  )
}


const Main = () => {

  return (
    <UserProvider>
    <BrowserRouter>
      <React.Fragment>
        <TopNavbar routes={myroutes} />
        <Row className="Main">
          <MainPage />
        </Row>
    </React.Fragment>
    </BrowserRouter>
    </UserProvider>
  );
}

export default Main;
