import React, { useState, useContext, useEffect } from "react";
import {
  Row,
  Col,
} from "react-bootstrap";

import { returnStatusCheck, getProfileInfo } from "../Services/authService";
import { UserContext } from "../UserContext/UserProvider";

const Profile = (props) => {
  const { user, dispatch } = useContext(UserContext);
  const viewingSelf = !(!!props.userId && props.userId != user.userId);
  const userId = !!viewingSelf ? user.userId : props.userId;
  const [ firstName, setFirstName ] = useState(!!viewingSelf ? user.firstName : null);
  const [ lastName, setLastName ] = useState(!!viewingSelf ? user.lastName : null);
  const [ userEmail, setUserEmail ] = useState(!!viewingSelf ? user.userEmail : null);
  const [ userTimezone, setUserTimezone ] = useState(!!viewingSelf ? user.userTimezone : null);
  const [ currentBadgeSet, setCurrentBadgeSet ] = useState(!!viewingSelf ? user.currentBadgeSet : null);


  useEffect(() => {
    getProfileInfo({forSelf: viewingSelf,
                    userId: userId,
                    dispatch: !!viewingSelf ? dispatch : null})
    .then(info => {
      returnStatusCheck(info, props.history,
        (info) => {
          console.log(info);
          setCurrentBadgeSet(info.currentBadgeSet);
        },
        dispatch
      )
    });
  },
  []);

  return (
    <Row className="profile-component content-view">
      <Col className="profile-info">
      <h2>My Profile</h2>
      <span className="profile-name">{firstName} {lastName}</span>
      <span className="profile-email">{userEmail}</span>
      <span className="profile-timezone">{userTimezone}</span>
      </Col>
      <h3>My Progress</h3>
      <Col className="profile-progress">
        So far I've reached badge set <span className="profile-progress-currentSet">{currentBadgeSet}</span>.
      </Col>
    </Row>
  )
}

export default Profile;
