import React, { useState, useContext, useEffect } from "react";
import {
  Row,
  Col,
  Tabs,
  Tab,
  Badge,
  Spinner,
  OverlayTrigger,
  Popover,
  PopoverTitle,
  PopoverContent
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { useHistory } from "react-router-dom";

import { returnStatusCheck, getProfileInfo } from "../Services/authService";
import { UserContext } from "../UserContext/UserProvider";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

const UpdateNotice = ({status}) => {
  return (status ? <span className="update-msg">
      <Spinner variant="secondary" animation="grow" size="sm" />Updating
    </span>
  : <span className="updated-msg"><FontAwesomeIcon icon="check-circle" />Up-to-date</span>
  )
}

const BadgeTerm = ({title, description, lessons}) => {
  const history = useHistory();
  return(
    <OverlayTrigger placement="auto"
      trigger="click"
      overlay={
        <Popover id={`tooltip-${title}`}>
          <PopoverTitle>
            <FontAwesomeIcon icon="certificate" />{title}
          </PopoverTitle>
          <PopoverContent>
            {`for ${description}`}
            <ul>
              {lessons.length != 0 && lessons.map(lesson =>
              <li key={lesson[0]}>
                <LinkContainer to={`/videos/${lesson[0]}`}>
                  <a className="lessonlink" >
                    <FontAwesomeIcon icon="video" />{lesson[1]}
                  </a>
                </LinkContainer>
              </li>
              )}
            </ul>
          </PopoverContent>
        </Popover>
      }
    >
      <Badge className={`profile badge badge-secondary badge-link`}>
        {title}
      </Badge>
    </OverlayTrigger>
  )
}

const Profile = (props) => {
  const { user, dispatch } = useContext(UserContext);
  const [ updating, setUpdating ] = useState(true);
  const viewingSelf = !(!!props.userId && props.userId != user.userId);
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
          setUpdating(false);
        },
        dispatch
      )
    });
  },
  []);

  const badgeLevelTitles = [
    {index: 1, slug: "level1", title: "Beginner",
     text: "I've just started learning these topics!"},
    {index: 2, slug: "level2", title: "Apprentice",
     text: "I've got a basic grasp of these topics!"},
    {index: 3, slug: "level3", title: "Journeyman",
     text: "I've got a good grasp of these topics!"},
    {index: 4, slug: "level4", title: "Master",
     text: "I've really got a solid mastery of these topics!"}
  ]

  return (
    <Row className="profile-component content-view">
      <Col className="profile-info" xs={12} lg={4}>
        <FontAwesomeIcon icon="user-circle" size="5x" />
        <span className="profile-name">{firstName} {lastName}</span><br />
        <span className="profile-email"><FontAwesomeIcon icon="envelope" />{userEmail}</span>&nbsp;
        <span className="profile-timezone"><FontAwesomeIcon icon="globe-americas" />{userTimezone}</span>
      </Col>
      <Col className="profile-progress" xs={12} lg={8}>
        <h3>My Progress</h3>
        <UpdateNotice status={updating} />
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
          <UpdateNotice status={updating} />
          <Tabs defaultActiveKey="level1" id="profile-stages-tabs">
            {( badgeLevels != null ) ? badgeLevelTitles.map(blevel =>
              <Tab
                key={blevel.slug}
                eventKey={blevel.slug}
                title={<React.Fragment><Badge variant="primary">{badgeLevels[blevel.index].length}</Badge> {blevel.title}</React.Fragment>}
              >
                <span className="level-explanation">{blevel.text}. (Click a badge for details.)</span>
                {badgeLevels[blevel.index].length != 0 && badgeLevels[blevel.index].map(b =>
                  <BadgeTerm key={b[0]} title={b[0]} description={b[2]} lessons={b[3]} />
                  )
                }
              </Tab>
            )
            : <div className="tab-pane active show">
              <Spinner variant="secondary" animation="grow" size="lg" />
              </div>}
          </Tabs>
      </Col>
    </Row>
  )
}

export default Profile;
