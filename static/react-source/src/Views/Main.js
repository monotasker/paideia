import React, { Component } from 'react';
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

// import './Main.css';
import './Main.scss';

import PrivateRoute from "../Components/PrivateRoute";
import TopNavbar from "../Components/TopNavbar";
import Home from "./Home";
import Login from "./Login";
import Walk from "./Walk";
import Profile from "./Profile";
import Videos from "./Videos";
import Info from "./Info";
import Admin from "./Admin";
import Instructors from "./Instructors";
import UserProvider from "../UserContext/UserProvider";

class Main extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activePath: {
        activeStep: {},
        completedSteps: [],
        remainingSteps: []
      },
      completedPaths: [],
      chosenPaths: [],
      currentLoc: null,
      previousLoc: null,
    }
  }

  render() {
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
            <Col className="content">
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
            </Col>
          </Row>
      </React.Fragment>
      </BrowserRouter>
      </UserProvider>
    );
  }
}

export default Main;
