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
import {
  faHome,
  faMap,
  faVideo,
  faSignInAlt,
  faUser,
  faInfoCircle,
  faWrench,
  faChalkboardTeacher,
  faQuestionCircle,
  faKeyboard,
  faCog,
  faBug,
  faSignOutAlt
} from '@fortawesome/free-solid-svg-icons';
import { logout } from '../Services/authService';
import { UserContext } from "../UserContext/UserProvider";

const navData = [
  {title: "Home", path: "/", icon: faHome},
  {title: "Map", path: "/walk/map", icon: faMap},
  {title: "Lessons", path: "/videos", icon: faVideo}
]

const dropData = [
  {label: "Info",
   icon: faInfoCircle,
   links: [{title: "FAQs",
            path: "/info/faq", icon: faQuestionCircle},
           {title: "Typing Greek",
            path: "/info/typing-greek", icon: faKeyboard},
           {title: "How It Works",
            path: "/info/how-it-works", icon: faCog},
           {title: "Known Bugs",
            path: "/info/known-bugs", icon: faBug},
          ],
   },
  {label: "Admin",
   icon: faWrench,
   links: [{title: "Home",
            path: "/", icon: faHome}
          ]
   },
  {label: "Instructors",
   icon: faChalkboardTeacher,
   links: [{title: "Home",
            path: "/", icon: faHome}
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
      <FontAwesomeIcon icon={faSignInAlt} size="sm" />
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
          <FontAwesomeIcon icon={faUser} size="sm" />
          <span className="d-none d-lg-inline">Profile</span>
        </Nav.Link>
      </LinkContainer>
      <LinkContainer key={`logout-${user.userId}`} to="/">
        <Nav.Link onClick={doLogout} >
          <FontAwesomeIcon icon={faSignOutAlt} size="sm" />
          <span className="d-none d-lg-inline">Log out</span>
        </Nav.Link>
      </LinkContainer>
      </React.Fragment>
    )

    return(
      <Navbar bg="light" expand="sm" className="fixed">
          <LinkContainer to="/">
            <Navbar.Brand>Paideia</Navbar.Brand>
          </LinkContainer>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mr-auto">
              {navs}
              {drops}
              {user.userLoggedIn != false ? welcome : login}
            </Nav>
          </Navbar.Collapse>
      </Navbar>
    )
}

export default withRouter(TopNavbar);
