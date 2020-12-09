import React, { useState, useContext, useEffect } from "react";
import {
  Col,
  Badge,
  Button,
  Form,
  InputGroup,
  OverlayTrigger,
  Popover,
  PopoverTitle,
  PopoverContent,
  Row,
  Spinner,
  Tab,
  Table,
  Tabs
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { useHistory } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { urlBase } from "../variables";
import { returnStatusCheck, getProfileInfo } from "../Services/authService";
import { UserContext } from "../UserContext/UserProvider";
import Calendar from "../Components/Calendar";
import { withinOneDay } from "../Services/dateTimeService";

const UpdateNotice = ({status}) => {
  return (status ? <span className="update-msg">
      <Spinner variant="secondary" animation="grow" size="sm" />Updating
    </span>
  : <span className="updated-msg"><FontAwesomeIcon icon="check-circle" />Up-to-date</span>
  )
}

const BadgeTerm = ({title, description, lessons, data, level}) => {
  const history = useHistory();
  return(
    <OverlayTrigger placement="auto" trigger="click" rootClose
      overlay={
        <Popover id={`tooltip-${title}`}>
          <PopoverTitle>
            <FontAwesomeIcon icon="certificate" />{title}
            <span className="badge-popover-level">{level}</span>
          </PopoverTitle>
          <PopoverContent>
            {`for ${description}`}
            <ul>
              {lessons.length != 0 && lessons.map(lesson =>
              <li key={lesson[0]}>
                <LinkContainer to={`/${urlBase}/videos/${lesson[0]}`}>
                  <a className="lessonlink" >
                    <FontAwesomeIcon icon="video" />{lesson[1]}
                  </a>
                </LinkContainer>
              </li>
              )}
            </ul>
            {data.curlev==1 && data.avg_score < 0.8 && data.rw_ratio < 5 &&
              <span className="badge-promotion-tip">Keep trying to get more of your responses right to raise your average score and have this badge promoted.</span>
            }
            {data.curlev==1 && (data.avg_score >= 0.8 || data.rw_ratio >= 5) && data.tright < 20 &&
              <span className="badge-promotion-tip">You're doing great. Just complete a {20 - data.tright} more right attempts with this badge to have it promoted.</span>
            }
            {data.curlev==1 && (data.avg_score >= 0.8 || data.rw_ratio >= 5) && data.tright >= 20 && data.delta_r > (30*3600*24) &&
              <span className="badge-promotion-tip">You've done great in the past. Just complete a right attempt again now to have it promoted.</span>
            }
            {data.curlev==1 && (data.avg_score >= 0.8 || data.rw_ratio >= 5) && data.tright >= 20 && withinOneDay(data.cat1_reached[0]) &&
              <span className="badge-promotion-tip">You've done great job so far. You just can't begin and promote a badge within the same day. Keep it up and this badge should be promoted tomorrow!</span>
            }
            {data.curlev!=1 && data.revlev == 1 &&
              <span className="badge-promotion-tip">This badge is due for some review to keep it fresh.</span>
            }
            <Table borderless hover size="sm">
                <tbody>
                  <tr>
                    <td>Recent average score</td>
                    {data.curlev==1 && data.avg_score >= 0.8 ?
                      <td className="target-reached">{data.avg_score}<FontAwesomeIcon icon="check-circle" /></td>
                      :
                      <td>{data.avg_score}</td>
                    }
                  </tr>
                  <tr>
                    <td><FontAwesomeIcon icon="check-circle" />Total right attempts</td>

                    {data.curlev==1 && data.tright >= 20 ?
                      <td className="target-reached">{data.tright}<FontAwesomeIcon icon="check-circle" /></td>
                      :
                      <td>{data.tright}</td>
                    }
                  </tr>
                  <tr>
                    <td><FontAwesomeIcon icon="times-circle" />Total wrong attempts</td>
                    <td>{data.twrong}</td>
                  </tr>
                  <tr>
                    <td><FontAwesomeIcon icon="balance-scale" />Right attempts per wrong attempt</td>
                    <td>{data.rw_ratio}</td>
                  </tr>
                  <tr>
                    <td><FontAwesomeIcon icon="clock" />Days since last right</td>
                    <td>{Math.floor(data.delta_r / (3600*24))}</td>
                  </tr>
                  <tr>
                    <td><FontAwesomeIcon icon="clock" />Days since last wrong</td>
                    <td>{Math.floor(data.delta_w / (3600*24))}</td>
                  </tr>
                  {[data.cat1_reached, data.cat2_reached, data.cat3_reached, data.cat4_reached].map((a, idx) => !!a && !!a[0] &&
                    <tr key={`promdate_${data.tag}_cat${idx + 1}`}>
                      <td><FontAwesomeIcon icon="flag" />
                        Reached {["beginner", "apprentice", "journeyman", "master"][idx]} level</td>
                      <td>{a[1]}</td>
                    </tr>
                  )}
                </tbody>
            </Table>
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

const ProfileCalendar = ({xs, lg, updating, calendarData, calYear, calMonth,
                          userId, dailyQuota, weeklyQuota}) => {
  return (
      <Col className="profile-calendar" xs={xs} lg={lg}>
        <h3>My Activity</h3>
        <UpdateNotice status={updating} />
        {calendarData &&
          <Calendar year={calYear} month={calMonth}
            user={userId} monthData={calendarData.data}
            dailyQuota={dailyQuota}
            weeklyQuota={weeklyQuota}
            parentUpdating={updating}
          />
        }
        {/*  TODO: Implement this user-set system of targets
        <InputGroup className="profile-calendar-targets-daily">
            <InputGroup.Prepend>
              <InputGroup.Text id="daytarget-label">Daily target</InputGroup.Text>
            </InputGroup.Prepend>
            <Form.Control
              placeholder={dailyQuota}
              aria-label="paths completed per day"
              aria-describedby="daytarget-label"
            />
            <InputGroup.Append>
              <InputGroup.Text id="basic-addon2">paths per day</InputGroup.Text>
            </InputGroup.Append>
        </InputGroup>
        <InputGroup className="profile-calendar-targets-weekly">
            <InputGroup.Prepend>
              <InputGroup.Text id="weektarget-label">Weekly target</InputGroup.Text>
            </InputGroup.Prepend>
            <Form.Control
              placeholder={weeklyQuota}
              aria-label="days meeting the daily target per week"
              aria-describedby="weektarget-label"
            />
            <InputGroup.Append>
              <InputGroup.Text id="basic-addon2">days meeting that target each week</InputGroup.Text>
            </InputGroup.Append>
        </InputGroup>
        <span>Note that if you are enrolled in a course you can't lower your targets below the minimum set by your instructor.</span>

        */}
      </Col>
    )
}

const Profile = (props) => {
  const myDate = new Date();
  const { user, dispatch } = useContext(UserContext);
  const [ updating, setUpdating ] = useState(true);
  const viewingSelf = !(!!props.userId && props.userId != user.userId);
  const userId = !!viewingSelf ? user.userId : props.userId;
  const dailyQuota = !!viewingSelf ? user.dailyQuota : props.dailyQuota;
  const weeklyQuota = !!viewingSelf ? user.weeklyQuota : props.weeklyQuota;
  const [ firstName, setFirstName ] = useState(
    !!viewingSelf ? user.firstName : null);
  const [ lastName, setLastName ] = useState(
    !!viewingSelf ? user.lastName : null);
  const [ userEmail, setUserEmail ] = useState(
    !!viewingSelf ? user.userEmail : null);
  const [ userTimezone, setUserTimezone ] = useState(
    !!viewingSelf ? user.userTimezone : null);
  const [ currentBadgeSet, setCurrentBadgeSet ] = useState(
    !!viewingSelf ? user.currentBadgeSet : null);
  const [ scaleBadgeSet, setScaleBadgeSet ] = useState(1);
  const [ badgeLevels, setBadgeLevels ] = useState(
    !!viewingSelf ? user.badgeLevels : null);
  const [ calendarData, setCalendarData ] = useState(
    !!viewingSelf ? user.calendar : null);
  const [ badgeTableData, setBadgeTableData ] = useState(
    !!viewingSelf ? user.badgeTableData : null);
  const [ answerCounts, setAnswerCounts ] = useState(
    !!viewingSelf ? user.answerCounts : null);
  const [ badgeSetDict, setBadgeSetDict ] = useState(
    !!viewingSelf ? user.badgeSetDict : null);
  const [ badgeSetMilestones, setBadgeSetMilestones ] = useState(
    !!viewingSelf ? user.badgeSetMilestones : null);
  const [ chart1Data, setChart1Data ] = useState(
    !!viewingSelf ? user.chart1Data : null);
  const [ calYear, setCalYear ] = useState(myDate.getFullYear());
  const [ calMonth, setCalMonth ] = useState(myDate.getMonth());

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
          setCalendarData(info.calendar);
          setBadgeTableData(info.badgeTableData);
          setAnswerCounts(info.answerCounts);
          setBadgeSetDict(info.badgeSetDict);
          setBadgeSetMilestones(info.badgeSetMilestones);
          setChart1Data(info.chart1Data);
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

      <ProfileCalendar xs={12} lg={4}
        updating={updating}
        calendarData={calendarData}
        calYear={calYear}
        calMonth={calMonth}
        userId={userId}
        dailyQuota={dailyQuota}
        weeklyQuota={weeklyQuota}
      />

      <Col className="profile-classinfo">
        <h3>My Class Group</h3>
        <UpdateNotice status={updating} />
        {user.classInfo === null ?
         <Spinner animation="grow" variant="secondary" />
         : (Object.keys(user.classInfo).length > 0 ?
              <Table className="profile-classinfo-content">
                <tbody>
                  <tr><td colSpan="2">
                    <span className="profile-classinfo-institution">{user.classInfo.institution}</span>,
                    <span className="profile-classinfo-section">
                    {user.classInfo.course_section}</span>,
                    <span className="profile-classinfo-term">
                    {user.classInfo.term} {user.classInfo.academic_year}
                    </span>
                  </td></tr>
                  <tr>
                    <td colSpan="2">start: {user.classInfo.start_date}, end: {user.classInfo.end_date}</td>
                  </tr>
                  <tr>
                    <td colSpan="2">Minimum participation requirements:
                      <ul>
                        <li>At least {user.classInfo.paths_per_day} paths each day</li>
                        <li>On at least {user.classInfo.days_per_week} different days</li>
                      </ul>
                    </td>
                  </tr>
                  <tr>
                    <td>A</td>
                    <td>badge set {Math.min(user.classInfo.a_cap, user.classInfo.a_target + user.classInfo.starting_set)}</td>
                  </tr>
                  <tr>
                    <td>B</td>
                    <td>badge set {Math.min(user.classInfo.b_cap, user.classInfo.b_target + user.classInfo.starting_set)}</td>
                  </tr>
                  <tr>
                    <td>C</td>
                    <td>badge set {Math.min(user.classInfo.c_cap, user.classInfo.c_target + user.classInfo.starting_set)}</td>
                  </tr>
                  <tr>
                    <td>D</td>
                    <td>badge set {Math.min(user.classInfo.d_cap, user.classInfo.d_target + user.classInfo.starting_set)}</td>
                  </tr>
                </tbody>
              </Table>
            : <React.Fragment>
                <div className="profile-classinfo-signup">
                You're not currently part of a class group in Paideia. If you have a class enrollment code, you can enter it here to join the class group.
                </div>
                <Form>
                  <Form.Row>
                    <Col>
                      <Form.Control type="text" placeholder="Enter code here" />
                    </Col>
                    <Col>
                      <Button variant="primary" type="submit">Join</Button>
                    </Col>
                  </Form.Row>
                </Form>
              </React.Fragment>
            )
        }
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
                {badgeLevels[blevel.index].length != 0 && badgeLevels[blevel.index].map(b => {
                  if (!!badgeTableData) {
                    const bData = badgeTableData.find(o => o.tag == b[1]);
                    return (
                      <BadgeTerm key={b[0]} title={b[0]} description={b[2]} lessons={b[3]} data={bData} level={blevel.title} />
                    )
                  }
                  })
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
