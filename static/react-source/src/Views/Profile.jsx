import React, { useState, useContext, useEffect } from "react";
import {
  Row,
  Col,
  Tabs,
  Tab,
  Spinner,
  Badge
} from "react-bootstrap";

import { returnStatusCheck, getProfileInfo } from "../Services/authService";
import { UserContext } from "../UserContext/UserProvider";

const Profile = (props) => {
  const { user, dispatch } = useContext(UserContext);
  const viewingSelf = !(!!props.userId && props.userId != user.userId);
  console.log('viewing self');
  console.log(viewingSelf);
  const userId = !!viewingSelf ? user.userId : props.userId;
  const [ firstName, setFirstName ] = useState(!!viewingSelf ? user.firstName : null);
  const [ lastName, setLastName ] = useState(!!viewingSelf ? user.lastName : null);
  const [ userEmail, setUserEmail ] = useState(!!viewingSelf ? user.userEmail : null);
  const [ userTimezone, setUserTimezone ] = useState(!!viewingSelf ? user.userTimezone : null);
  const [ currentBadgeSet, setCurrentBadgeSet ] = useState(!!viewingSelf ? user.currentBadgeSet : null);
  const [ scaleBadgeSet, setScaleBadgeSet ] = useState(1);
  const [ badgeLevels, setBadgeLevels ] = useState(!!viewingSelf ? user.badgeLevels : null);
  console.log('badge levels');
  console.log(badgeLevels);

  useEffect(() => {
    window.setTimeout(2000);
    setScaleBadgeSet(currentBadgeSet);
  }, [currentBadgeSet])

  useEffect(() => {
    getProfileInfo({forSelf: viewingSelf,
                    userId: userId,
                    dispatch: !!viewingSelf ? dispatch : null})
    .then(info => {
      returnStatusCheck(info, props.history,
        (info) => {
          console.log(info);
          setCurrentBadgeSet(info.currentBadgeSet);
          setBadgeLevels(info.badgeLevels);
        },
        dispatch
      )
    });
  },
  []);

  const badgeLevelTitles = [
    {index: 1, slug: "level1", title: "Beginner"},
    {index: 2, slug: "level2", title: "Apprentice"},
    {index: 3, slug: "level3", title: "Journeyman"},
    {index: 4, slug: "level4", title: "Master"}
  ]

  return (
    <Row className="profile-component content-view">
      <Col className="profile-info" xs={12} lg={4}>
        <h2>My Profile</h2>
        <span className="profile-name">{firstName} {lastName}</span>&nbsp;
        <span className="profile-email">{userEmail}</span>&nbsp;
        <span className="profile-timezone">{userTimezone}</span>&nbsp;
      </Col>
      <Col className="profile-progress" xs={12} lg={8}>
        <h3>My Progress</h3>
        .
        <div className="profile-progress-scale-container">
          <div className="profile-progress-scale">
            {Array.from('x'.repeat(20), (_, i) => 1 + i).map(n =>
              <div key={n} className="profile-progress-unit">{n}
                {n == scaleBadgeSet &&
                <div className="current-set">
                  <span className="current-set-intro">
                    So far I've reached badge set</span>
                  <span className="current-set-number">{n}</span>
                </div>}
              </div>
            )}
          </div>
          <div className={`profile-progress-bar badge-set-${scaleBadgeSet}`}>
            {Array.from('x'.repeat(20), (_, i) => 1 + i).map(n =>
              <div key={n} className="profile-progress-unit">{n}
              </div>
            )}
          </div>
        </div>

      </Col>
      <Col className="profile-stages">
        <h3>My Badge Mastery</h3>
          <Tabs defaultActiveKey="level1" id="profile-stages-tabs">
            {(!!badgeLevels && badgeLevels.length != 0) ? badgeLevelTitles.map(blevel =>
              <Tab
                key={blevel.slug}
                eventKey={blevel.slug}
                title={<React.Fragment><Badge variant="primary">{badgeLevels[blevel.index].length}</Badge> {blevel.title}</React.Fragment>}
              >
                {badgeLevels[blevel.index].length != 0 && badgeLevels[blevel.index].map(b => <Badge key={b[0]}>{b[0]}</Badge>)
                }
              </Tab>
            ) : <Spinner animation="grow" />}
          </Tabs>
      </Col>
    </Row>
  )
}

export default Profile;
