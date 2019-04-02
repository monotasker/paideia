import React, { Component } from 'react';
import styled from "styled-components";
import {
  Container,
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
  faBug
} from '@fortawesome/free-solid-svg-icons';

const TopNav = styled(Navbar)`
  background-color: #fff;
  box-shadow: 0 3px 0 rgba(0, 0, 0, 0.2);
  line-height: 1;
  a.navbar-brand         {text-transform: uppercase;
                          letter-spacing: 2px;
                          color: $danger;
                          transition: 100ms all linear;
                          font-family: 'Amatic SC', cursive;
                          font-weight: normal;
                          font-size: 3rem;
      &:hover            {color: lighten($danger, 10%);
                          transition: 100ms all linear;
      }
  }
  small                  {display: none;
  }
  a                      {color: #aaa;
  }
  .navbar-toggle span    {background-color: #aaa;
  }
  .navbar-nav            {
      >a                 {
          &:hover,
          &:active,
          &.open        {color: $white;
                         background-color: lighten($accent2, 20%);
      }
        .dropdown-menu {
            top: -2px;
            background-color: lighten($accent2, 20%);
            border: 1px solid lighten($accent2, 10%);
            li            {
                &.divider {background-color: lighten($accent2, 10%);
                             margin: 0;
                  }
                  a         {color: $white;
                             line-height: 3em;
                             height: 3em;
                             padding-top: 0;
                             padding-bottom: 0;
                      &:hover,
                      &:active    {background-color: lighten($accent2, 10%);
                      }
                  }
              }
          }
      }
  }
  .badge-wrapper         {height: 100%;
                          line-height: 100%;
                          float: right;
                          position: relative;
                          display: block;
      #unread-counter    {border-radius: 0;
                          color: $pallette3;
                          height: 100%;
                          line-height: 100%;
                          padding: 19px;
                          background-color: lighten($pallette3, 40%);
                          transition: all .3s ease-in-out;
          &:hover        {background-color: lighten($pallette3, 45%);
                          columns: darken($pallette3, 10%);
                          transition: all .5s ease-in-out;
          }
      }
  }
`;

const navData = [
  {title: "Home", path: "/", icon: faHome},
  {title: "Map", path: "/walk/map", icon: faMap},
  {title: "Lessons", path: "/videos", icon: faVideo},
  {title: "Profile", path: "/profile", icon: faUser}
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

class TopNavbar extends Component {
  constructor(props){
    super(props);
    this.state = {};
  }

  render(){
    return(
      <TopNav bg="light" expand="md" className="fixed">
        <Container>
          <LinkContainer to="/">
            <Navbar.Brand>Paideia</Navbar.Brand>
          </LinkContainer>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="mr-auto">
              {navs}
              {drops}
              <LinkContainer to="/login">
                <Nav.Link href="/login">
                  <FontAwesomeIcon icon={faSignInAlt} size="sm" />
                  Log in
                </Nav.Link>
              </LinkContainer>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </TopNav>
    )
  }
}

export default TopNavbar;
