import React, { Component } from 'react';
import {
  Container,
  Row,
  Col,
} from "react-bootstrap";
import {
  Switch,
  Route,
  BrowserRouter
} from "react-router-dom";
import { TransitionGroup, Transition } from "react-transition-group";
import { TimelineLite, CSSPlugin } from "gsap";

import './Main.css';
import './Main.scss';

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
    return (
      <UserProvider>
      <BrowserRouter>
        <div className="Main">
          <TopNavbar />
          <Row>
            <Col className="content">
              <Route render={ ({location}) => {
                const {pathname, key} = location;
                return(
                  <TransitionGroup component={null}>
                    <Transition
                      key={key}
                      appear={true}
                      onEnter={(node, appears) => this.play(pathname, node, appears)}
                      timeout={{enter: 750, exit: 0}}
                    >
                      <Switch location={location.location}>
                        <Route exact path="/" component={Home}/>
                        <Route path="/walk" component={Walk}/>
                        <Route path="/videos" component={Videos}/>
                        <Route path="/profile" component={Profile}/>
                        <Route path="/info/:infoPage" component={Info}/>
                        <Route path="/admin/:adminPage" component={Admin}/>
                        <Route path="/instructors/:instrPage"
                          component={Instructors}/>
                        <Route path="/login" component={Login}/>
                      </Switch>
                    </Transition>
                  </TransitionGroup>
                )
              }} />
            </Col>
          </Row>
        </div>
      </BrowserRouter>
      </UserProvider>
    );
  }
}

export default Main;
