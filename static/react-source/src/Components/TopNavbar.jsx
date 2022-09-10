import React, { useContext } from 'react';
import { useHistory } from "react-router-dom";
import {
  Navbar,
  Nav,
  NavDropdown
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { logout } from '../Services/authService';
import { UserContext } from "../UserContext/UserProvider";
import { urlBase } from "../variables";



const NavLink = ({title, path, icon, displayAt, ...rest}) => {
  const extraDisplay = displayAt === "lg" ? "d-sm-none" : "";
  return(
    <LinkContainer key={title} to={`/${urlBase}${path}`} {...rest}>
      <Nav.Link>
        <FontAwesomeIcon icon={icon} size="sm" />
        <span className={`${extraDisplay} d-${displayAt}-inline`}>{title}</span>
      </Nav.Link>
    </LinkContainer>
  )
}

const MyDropdown = ({label, icon, children}) => {
  return(
    <NavDropdown
      title={
        <React.Fragment>
          <FontAwesomeIcon icon={icon} />
          <span className="d-sm-none d-lg-inline">{label}</span>
        </React.Fragment>
      }
      id={`nav-dropdown-${label}`}
    >
      {children}
    </NavDropdown>
  )
}

const TopNavbar = ({pageLoaded, ...props}) => {
    const { user, dispatch } = useContext(UserContext);

    const doLogout = () => {
      logout()
      .then(response => {
        if (!response.id) {
          dispatch({type: 'deactivateUser', payload: user.userId});
        } else {
          console.log("failed to log out from server!");
        }
      });
    }


    return(
      <Navbar bg="light" expand="sm" fixed="top"
        className={`${!!pageLoaded ? "page-loaded" : ""}`}
      >
          <LinkContainer to={`/${urlBase}/`}>
            <Navbar.Brand>Paideia</Navbar.Brand>
          </LinkContainer>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mr-auto main-nav">
              <NavLink title="Home" path="/home" icon='home' displayAt="lg" />
              <NavLink title="Map" path="/walk/map" icon='map' displayAt="lg" />
              <NavLink title="Lessons" path="/videos" icon='video' displayAt="lg" />
              {user.userRoles &&
               ['instructors', 'administrators'].some(e => user.userRoles.includes(e)) &&
                <NavLink title="Instructors"
                  path="/instructors/dashboard"
                  icon='chalkboard-teacher' displayAt="lg"
                />
              }
              <MyDropdown label="Info" icon='info-circle' >
                <NavLink title="FAQs" path="/info/faq" icon='question-circle' displayAt="sm" />
                <NavLink title="Typing Greek" path="/info/typing-greek" icon='keyboard'  displayAt="sm" />
                <NavLink title="How It Works" path="/info/how-it-works" icon='cog'  displayAt="sm" />
                <NavLink title="Known Bugs" path="/info/known-bugs" icon='bug'  displayAt="sm" />
              </MyDropdown>
              {user.userRoles && user.userRoles.includes('administrators') &&
              <MyDropdown label="Admin" icon='wrench' >
                <NavLink title="Classes" path="/admin/classes" icon='home'  displayAt="sm" />
                <NavLink title="Paths" path="/admin/paths" icon='home'  displayAt="sm" />
              </MyDropdown>
              }
            </Nav>
            <Nav className="welcome-nav">
              {user.userLoggedIn != false ?
                <React.Fragment>
                  <span className="navbar-welcome">Hi {user.firstName}</span>
                  <NavLink title="Profile" path="/profile" icon="user" displayAt="lg" />
                  <NavLink title="Log out" path="/" icon="sign-out-alt"
                    onClick={doLogout} displayAt="lg" />
                </React.Fragment>
               : <React.Fragment>
                  <NavLink title="Log in" path="/login" icon="sign-in-alt" displayAt="sm" />
                  <NavLink title="Sign up" path="/register" icon="user-plus" displayAt="sm" />
                </React.Fragment>
              }
            </Nav>
          </Navbar.Collapse>
      </Navbar>
    )
}

export default TopNavbar;
