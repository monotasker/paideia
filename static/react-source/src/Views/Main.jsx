import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import {
  Row,
  Col,
} from "react-bootstrap";
import {
  Switch,
  Route,
  BrowserRouter
} from "react-router-dom";
import { CSSTransition } from "react-transition-group";
import { library } from '@fortawesome/fontawesome-svg-core';
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faArrowsAltH,
  faBolt,
  faBug,
  faChalkboardTeacher,
  faCheckCircle,
  faCog,
  faComment,
  faFilter,
  faFont,
  faGlobeAmericas,
  faHistory,
  faHome,
  faInfoCircle,
  faKeyboard,
  faQuestionCircle,
  faRedoAlt,
  faMap,
  faPencilAlt,
  faSearch,
  faSignInAlt,
  faSignOutAlt,
  faSort,
  faSortUp,
  faSortDown,
  faSortAlphaDown,
  faSpinner,
  faUser,
  faUserCircle,
  faUsers,
  faVideo,
  faWalking,
  faWrench,
} from '@fortawesome/free-solid-svg-icons';

// import './Main.css';
import './Main.scss';

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
import UserProvider from "../UserContext/UserProvider";

library.add(
  faArrowsAltH,
  faBolt,
  faBug,
  faChalkboardTeacher,
  faCheckCircle,
  faCog,
  faComment,
  faFilter,
  faFont,
  faGlobeAmericas,
  faHistory,
  faHome,
  faInfoCircle,
  faKeyboard,
  faPencilAlt,
  faQuestionCircle,
  faRedoAlt,
  faMap,
  faSearch,
  faSignInAlt,
  faSignOutAlt,
  faSort,
  faSortAlphaDown,
  faSortUp,
  faSortDown,
  faSpinner,
  faUser,
  faUserCircle,
  faUsers,
  faVideo,
  faWalking,
  faWrench,
);

const Main = (props) => {

    const [ myheight, setMyheight ] = useState(null);

    const setHeight = () => {
      const headroom = document.querySelector('.navbar').offsetHeight;
      let divheight = window.innerHeight - headroom;
      setMyheight(divheight);
    }

    useEffect(() => {
      setHeight();
    });

    const myroutes = [
      {path: "/(paideia/static/react-source/dist/index.html|)", exact: true, Component: Home},
      // {path: "/walk/:walkPage", exact: false, Component: Walk},
      {path: "/videos", exact: false, Component: Videos},
      {path: "/profile", exact: false, Component: Profile},
      {path: "/info/:infoPage", exact: false, Component: Info},
      {path: "/admin/:adminPage", exact: false, Component: Admin},
      {path: "/instructors/:instrPage", exact: false, Component: Instructors},
      {path: "/login", exact: false, Component: Login}
    ]

    return (
      <UserProvider>
      <BrowserRouter>
        <React.Fragment>
          <TopNavbar routes={myroutes} />
          <Row className="Main">
            <Col className="content"
              style={{height: myheight}}
            >
              <Switch>
                <PrivateRoute exact={false} path="/walk/:walkPage" >
                  <Walk />
                </PrivateRoute>
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
                      <Component />
                    </CSSTransition>
                  )}
                </Route>
              )
              )}
              </Switch>
              <Tools />
            </Col>
          </Row>
      </React.Fragment>
      </BrowserRouter>
      </UserProvider>
    );
}

export default Main;
