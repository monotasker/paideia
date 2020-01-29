import React, { useContext } from 'react';
import { withRouter } from "react-router";
import styled from "styled-components";
import {
  Navbar,
  Nav,
  NavDropdown
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { logout } from '../Services/authService';
import { UserContext } from "../UserContext/UserProvider";

const navData = [
  {title: "Home", path: "/", icon: 'home'},
  {title: "Map", path: "/walk/map", icon: 'map'},
  {title: "Lessons", path: "/videos", icon: 'video'}
]

const dropData = [
  {label: "Info",
   icon: 'info-circle',
   links: [{title: "FAQs",
            path: "/info/faq", icon: 'question-circle'},
           {title: "Typing Greek",
            path: "/info/typing-greek", icon: 'keyboard'},
           {title: "How It Works",
            path: "/info/how-it-works", icon: 'cog'},
           {title: "Known Bugs",
            path: "/info/known-bugs", icon: 'bug'},
          ],
   },
  {label: "Admin",
   icon: 'wrench',
   links: [{title: "Home",
            path: "/", icon: 'home'}
          ]
   },
  {label: "Instructors",
   icon: 'chalkboard-teacher',
   links: [{title: "Home",
            path: "/", icon: 'home'}
           ]
   }
]

const navs = navData.map( (item) =>
  <LinkContainer key={item.title} to={item.path}>
    <Nav.Link>
      <FontAwesomeIcon icon={item.icon} size="sm" />
      <span className="d-none d-lg-inline">{item.title}</span>
    </Nav.Link>
  </LinkContainer>
);

const drops = dropData.map( (item) =>
  <NavDropdown
    key={item.label}
    title={
      <span>
        <FontAwesomeIcon icon={item.icon} />
        <span className="d-none d-xl-inline">{item.label}</span>
      </span>
    }
    id="basic-nav-dropdown"
    >
    {item.links.map( (link) =>
      <LinkContainer key={link.title} to={link.path}>
        <NavDropdown.Item>
          <FontAwesomeIcon icon={link.icon} size="sm" />
          {link.title}
        </NavDropdown.Item>
      </LinkContainer>
    )}
  </NavDropdown>
);

const login = (
  <LinkContainer to="/login">
    <Nav.Link href="/login">
      <FontAwesomeIcon icon='sign-in-alt' size="sm" />
      Log in
    </Nav.Link>
  </LinkContainer>
)


const TopNavbar = () => {
    const { user, dispatch } = useContext(UserContext);

    const doLogout = () => {
      logout();
      dispatch({type: 'deactivateUser', payload: null});
    }

    const welcome = (
      <React.Fragment>
      <span>Hi {user.firstName}</span>
      <LinkContainer key={user.userId} to="/profile">
        <Nav.Link>
          <FontAwesomeIcon icon='user' size="sm" />
          <span className="d-none d-lg-inline">Profile</span>
        </Nav.Link>
      </LinkContainer>
      <LinkContainer key={`logout-${user.userId}`} to="/">
        <Nav.Link onClick={doLogout} >
          <FontAwesomeIcon icon='sign-out-alt' size="sm" />
          <span className="d-none d-lg-inline">Log out</span>
        </Nav.Link>
      </LinkContainer>
      </React.Fragment>
    )

    return(
      <Navbar bg="light" expand="sm" className="fixed">
          <LinkContainer to="/">
            <Navbar.Brand>Greektown</Navbar.Brand>
          </LinkContainer>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mr-auto main-nav">
              {navs}
              {drops}
            </Nav>
            <Nav className="welcome-nav">
              {user.userLoggedIn != false ? welcome : login}
            </Nav>
          </Navbar.Collapse>
      </Navbar>
    )
}

export default withRouter(TopNavbar);
