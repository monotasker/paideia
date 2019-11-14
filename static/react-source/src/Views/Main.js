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
import styled, { ThemeProvider } from "styled-components";
import { Transition } from "react-transition-group";
import { TimelineLite } from "gsap";

// import './Main.css';
// import './Main.scss';

import TopNavbar from "../Components/TopNavbar"
import Home from "./Home";
import Login from "./Login";
import Walk from "./Walk";
import Profile from "./Profile";
import Videos from "./Videos";
import Info from "./Info";
import Admin from "./Admin";
import Instructors from "./Instructors";
import UserProvider from "../UserContext/UserProvider";
import {
  GlobalStyle,
  Theme
} from "../variables.js";

const Div = styled.div`
  // .content > div {margin-left: 0;
  //                 margin-right: 0;
  // 12:25 PM}
`;

function FirstChild(props) {
  const childrenArray = React.Children.toArray(props.children);
  return childrenArray[0] || null;
}

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
    this.play = this.play.bind(this);
  }

  play(pathname, node, appears) {
    console.log(node);
    console.log('pathname');
    console.log(pathname);
    const delay = appears ? 0 : 0.5;
    let timeline;

    if (pathname === '/') {
      timeline = this.getHomeTimeline(node, delay)
    } else {
      timeline = this.getDefaultTimeline(node, delay)
    }

    window.loadPromise.then(timeline.play());
  }

  getHomeTimeline(node, delay) {
    const timeline = new TimelineLite({ paused: true });
    // const texts = node.querySelectorAll('div.container');

    timeline
      .from(node, 0, { left: (window.innerWidth * -1) })
      .to(node, 1, { left: 0 });
      // .staggerFrom(texts, 0.375, { autoAlpha: 0, x: -25, ease: Power1.easeOut }, 0.125);

    return timeline;
  }

  getDefaultTimeline(node, delay) {
    const timeline = new TimelineLite({ paused: true });
    // const texts = node.querySelectorAll('div.container');

    timeline
      .from(node, 0, { left: (window.innerWidth * -1) })
      .to(node, 0.5, { left: 0 });
      // .staggerFrom(texts, 0.375, { autoAlpha: 0, x: -25, ease: Power1.easeOut }, 0.125);

    return timeline;
  }


  render() {
    const myroutes = [
      {path: "/(paideia/static/react-source/dist/index.html|)", exact: true, Component: Home},
      {path: "/walk/:walkPage", exact: false, Component: Walk},
      {path: "/videos", exact: false, Component: Videos},
      {path: "/profile", exact: false, Component: Profile},
      {path: "/info/:infoPage", exact: false, Component: Info},
      {path: "/admin/:adminPage", exact: false, Component: Admin},
      {path: "/instructors/:instrPage", exact: false, Component: Instructors},
      {path: "/login", exact: false, Component: Login}
    ]
    return (
      <ThemeProvider theme={Theme}>
      <UserProvider>
      <BrowserRouter>
        <React.Fragment>
        <GlobalStyle />
          <TopNavbar routes={myroutes} />
          <Row className="Main">
            <Col className="content">
              <Switch>
              {myroutes.map(({ path, exact, Component }) => (
                <Route key={path} exact={exact} path={path}>
                  {( match, location ) => (
                    <Transition
                      key={path}
                      in={match != null}
                      appear={true}
                      onEnter={(node, appears) => this.play(match.location.pathname, node, appears)}
                      timeout={{enter: 750, exit: 0}}
                      mountOnEnter
                      unmountOnExit
                    >
                      <Component />
                    </Transition>
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
      </ThemeProvider>
    );
  }
}

export default Main;
