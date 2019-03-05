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
  Route,
  NavLink,
  HashRouter
} from "react-router-dom";
import Home from "./Home";
import Walk from "./Walk";
import Profile from "./Profile";
import Videos from "./Videos";

class Main extends Component {
  render() {
    return (
      <HashRouter>
        <Container className="Main">
          <Navbar bg="light" expand="lg">
            <Navbar.Brand href="/">Paideia</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mr-auto">
              <Nav.Link href="#">Home</Nav.Link>
              <Nav.Link href="#walk">Walk</Nav.Link>
              <Nav.Link href="#profile">Profile</Nav.Link>
              <Nav.Link href="#videos">Videos</Nav.Link>
              <NavDropdown title="Dropdown" id="basic-nav-dropdown">
                <NavDropdown.Item href="#action/3.1">Action</NavDropdown.Item>
                <NavDropdown.Item href="#action/3.2">Another action</NavDropdown.Item>
                <NavDropdown.Item href="#action/3.3">Something</NavDropdown.Item>
                <NavDropdown.Divider />
                <NavDropdown.Item href="#action/3.4">Separated link</NavDropdown.Item>
              </NavDropdown>
            </Nav>
            </Navbar.Collapse>
          </Navbar>
          <Row>
            <Col>
              <div className="content">
                <Route exact path="/" component={Home}/>
                <Route path="/walk" component={Walk}/>
                <Route path="/profile" component={Profile}/>
                <Route path="/videos" component={Videos}/>
              </div>
            </Col>
          </Row>
        </Container>
      </HashRouter>
    );
  }
}

export default Main;
