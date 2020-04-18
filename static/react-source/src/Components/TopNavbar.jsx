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



const NavLink = ({title, path, icon, ...rest}) => {
  return(
    <LinkContainer key={title} to={path} {...rest}>
      <Nav.Link>
        <FontAwesomeIcon icon={icon} size="sm" />
        <span className="d-none d-lg-inline">{title}</span>
      </Nav.Link>
    </LinkContainer>
  )
}

const MyDropdown = ({label, icon, children}) => {
  return(
    <NavDropdown
      title={
        <span>
          <FontAwesomeIcon icon={icon} />
          <span className="d-none d-xl-inline">{label}</span>
        </span>
      }
      id={`nav-dropdown-${label}`}
    >
      {children}
    </NavDropdown>
  )
}

const TopNavbar = () => {
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

    const welcome = (
      <React.Fragment>
        <span>Hi {user.firstName}</span>
        <NavLink title="Profile" path="/profile" icon="user" />
        <NavLink title="Log out" path="/" icon="sign-out-alt"
          onClick={doLogout} />
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
              <NavLink title="Home" path="/" icon='home' />
              <NavLink title="Map" path="/walk/map" icon='map' />
              <NavLink title="Lessons" path="/videos" icon='video' />
              {user.userRoles &&
               ['instructors', 'administrators'].some(e => user.userRoles.includes(e)) &&
                <NavLink title="Instructors"
                  path="/instructors/dashboard"
                  icon='chalkboard-teacher'
                />
              }
              <MyDropdown label="Info" icon='info-circle' >
                <NavLink title="FAQs" path="/info/faq" icon='question-circle' />
                <NavLink title="Typing Greek" path="/info/typing-greek" icon='keyboard' />
                <NavLink title="How It Works" path="/info/how-it-works" icon='cog' />
                <NavLink title="Known Bugs" path="/info/known-bugs" icon='bug' />
              </MyDropdown>
              {user.userRoles && user.userRoles.includes('administrators') &&
              <MyDropdown label="Admin" icon='wrench' >
                <NavLink title="Class management" path="/admin/classes" icon='home' />
              </MyDropdown>
              }
            </Nav>
            <Nav className="welcome-nav">
              {user.userLoggedIn != false ? welcome
               : <NavLink title="Log in" path="/login" icon="sign-in-alt" />
              }
            </Nav>
          </Navbar.Collapse>
      </Navbar>
    )
}

export default TopNavbar;
