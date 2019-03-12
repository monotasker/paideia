import React, { Component } from 'react';
import './Main.css';
import {
  Container,
  Row,
  Col,
  Navbar,
  Nav,
  NavDropdown
} from "react-bootstrap";
import {
  Switch,
  Route,
  HashRouter
} from "react-router-dom";
import Home from "./Home";
import Login from "./Login";
import Walk from "./Walk";
import Profile from "./Profile";
import UserProvider from "../UserContext/UserProvider";
import Videos from "./Videos";

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
  };

  render() {
    return (
      <UserProvider>
      <HashRouter>
        <Container fluid className="Main">
          <Navbar bg="light" expand="lg">
            <Container>
            <Navbar.Brand href="/">Paideia</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mr-auto">
              <Nav.Link href="#">Home</Nav.Link>
              <Nav.Link href="#walk">Walk</Nav.Link>
              <Nav.Link href="#profile">Profile</Nav.Link>
              <Nav.Link href="#videos">Videos</Nav.Link>
              <NavDropdown title="Admin" id="basic-nav-dropdown">
                <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
              </NavDropdown>
              <NavDropdown title="Instructors" id="basic-nav-dropdown">
                <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
              </NavDropdown>
              <Nav.Link href="#login">Log in</Nav.Link>
            </Nav>
            </Navbar.Collapse>
            </Container>
          </Navbar>
          <Row>
            <Col className="content">
                <Switch>
                  <Route exact path="/" component={Home}/>
                  <Route path="/walk" component={Walk}/>
                  <Route path="/profile" component={Profile}/>
                  <Route path="/videos" component={Videos}/>
                  <Route path="/login" component={Login}/>
                </Switch>
            </Col>
          </Row>
        </Container>
      </HashRouter>
      </UserProvider>
    );
  }
}

export default Main;
