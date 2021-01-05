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
// import { LinkContainer } from "react-router-bootstrap";
import { useParams, Link } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { urlBase } from "../variables";
import { returnStatusCheck, getProfileInfo } from "../Services/authService";
import { UserContext } from "../UserContext/UserProvider";
import Calendar from "../Components/Calendar";
import { withinOneDay,
         readableDate
       } from "../Services/dateTimeService";

const UpdateNotice = ({status}) => {
  return (status ? <span className="update-msg">
      <Spinner variant="secondary" animation="grow" size="sm" />Updating
    </span>
  : <span className="updated-msg"><FontAwesomeIcon icon="check-circle" />Up-to-date</span>
  )
}

const BadgeTerm = ({title, description, lessons, data, level}) => {
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
              {lessons.length !== 0 && lessons.map(lesson =>
              <li key={lesson[0]}>
                <Button to={`/${urlBase}/videos/${lesson[0]}`}
                  className="lessonlink"
                  as={Link}
                >
                    <FontAwesomeIcon icon="video" />{lesson[1]}
                </Button>
              </li>
              )}
            </ul>
            {!!data && data.curlev===1 && data.avg_score < 0.8 && data.rw_ratio < 5 &&
              <span className="badge-promotion-tip">Keep trying to get more of your responses right to raise your average score and have this badge promoted.</span>
            }
            {!!data && data.curlev===1 && (data.avg_score >= 0.8 || data.rw_ratio >= 5) && data.tright < 20 &&
              <span className="badge-promotion-tip">You're doing great. Just complete a {20 - data.tright} more right attempts with this badge to have it promoted.</span>
            }
            {!!data && data.curlev===1 && (data.avg_score >= 0.8 || data.rw_ratio >= 5) && data.tright >= 20 && data.delta_r > (30*3600*24) &&
              <span className="badge-promotion-tip">You've done great in the past. Just complete a right attempt again now to have it promoted.</span>
            }
            {!!data && data.curlev===1 && (data.avg_score >= 0.8 || data.rw_ratio >= 5) && data.tright >= 20 && withinOneDay(data.cat1_reached[0]) &&
              <span className="badge-promotion-tip">You've done great job so far. You just can't begin and promote a badge within the same day. Keep it up and this badge should be promoted tomorrow!</span>
            }
            {!!data && data.curlev!==1 && data.revlev === 1 &&
              <span className="badge-promotion-tip">This badge is due for some review to keep it fresh.</span>
            }
            {!!data ? (
              <Table borderless hover size="sm">
                  <tbody>
                    <tr>
                      <td>Recent average score</td>
                      {data.curlev===1 && data.avg_score >= 0.8 ?
                        <td className="target-reached">{data.avg_score}<FontAwesomeIcon icon="check-circle" /></td>
                        :
                        <td>{data.avg_score}</td>
                      }
                    </tr>
                    <tr>
                      <td><FontAwesomeIcon icon="check-circle" />Total right attempts</td>

                      {data.curlev===1 && data.tright >= 20 ?
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
            )
              :
              <span>Couldn't find badge data!</span>
            }
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

  const userIdParam = parseInt(useParams().userId);
  console.log('userIdParam');
  console.log(userIdParam);
  const { user, dispatch } = useContext(UserContext);
  console.log('User in Profie ++++++++++++++');
  console.log(user);

  const [ updating, setUpdating ] = useState(true);
  const [ authorized, setAuthorized ] = useState(true);
  const [ recordExists, setRecordExists ] = useState(true);
  const viewingSelf = !userIdParam || userIdParam === user.userId;

  const userId = !!viewingSelf ? user.userId : userIdParam; // props.userId;
  const [ dailyQuota, setDailyQuota ] = useState(
    !!viewingSelf ? user.dailyQuota : null);
  const [ weeklyQuota, setWeeklyQuota ] = useState(
    !!viewingSelf ? user.weeklyQuota : null);
  const [ firstName, setFirstName ] = useState(
    !!viewingSelf ? user.firstName : "fetching");
  const [ lastName, setLastName ] = useState(
    !!viewingSelf ? user.lastName : "...");
  const [ userEmail, setUserEmail ] = useState(
    !!viewingSelf ? user.userEmail : "fetching...");
  const [ userTimezone, setUserTimezone ] = useState(
    !!viewingSelf ? user.userTimezone : "fetching...");
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
  const [ classInfo, setClassInfo ] = useState(
    !!viewingSelf ? user.classInfo : null);
  const [ calYear, setCalYear ] = useState(myDate.getFullYear());
  const [ calMonth, setCalMonth ] = useState(myDate.getMonth());

  const insufficientPrivilegesAction = (mydata) => {
    console.log('User cannot view this profile');
    setAuthorized(false);
  };

  const noRecordAction = (mydata) => {
    console.log('No record for the requested user.');
    setRecordExists(false);
  };

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

          setFirstName(info.firstName);
          setLastName(info.lastName);
          setUserEmail(info.email);
          setUserTimezone(info.timezone);
          setDailyQuota(!!info.pathsPerDay ? info.pathsPerDay : 20);
          setWeeklyQuota(!!info.daysPerWeek ? info.daysPerWeek : 5);
          setCurrentBadgeSet(info.currentBadgeSet);
          setBadgeLevels(info.badgeLevels);
          setCalendarData(info.calendar);
          setBadgeTableData(info.badgeTableData);
          setAnswerCounts(info.answerCounts);
          setBadgeSetDict(info.badgeSetDict);
          setBadgeSetMilestones(info.badgeSetMilestones);
          setChart1Data(info.chart1Data);
          setClassInfo(info.classInfo);
          setUpdating(false);
          /* FIXME: update course data in provider if viewing self and changed */
        },
        dispatch,
        {insufficientPrivilegesAction: insufficientPrivilegesAction,
         noRecordAction: noRecordAction}
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
      {!(authorized && recordExists) ? (
          !authorized ? <span>Sorry, you aren't authorized to view that studen's record. If you think you should be, please contact the site administrator.</span>
          : <span>Sorry, the requested user account does not exist.</span>
        )
      : (<React.Fragment>
        <Col className="profile-info" xs={12} lg={4}>
          {!viewingSelf && <Badge variant="warning">Viewing student info</Badge>}
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
          {/* FIXME: Update user.classInfo and this widget if enrollment discovered */}
          {!!updating ?
            <Spinner animation="grow" variant="secondary" />
            : (classInfo !== null && Object.keys(classInfo).length > 0 ?
                <Table className="profile-classinfo-content">
                  <tbody>
                    <tr><td colSpan="2">
                      <span className="profile-classinfo-institution">{classInfo.institution}</span>,&nbsp;
                      <span className="profile-classinfo-section">
                      {classInfo.course_section}</span>,&nbsp;
                      <span className="profile-classinfo-term">
                      {classInfo.term} {classInfo.academic_year}
                      </span>
                    </td></tr>
                    <tr>
                      <td colSpan="2">course start:&nbsp;
                      {readableDate(!!classInfo.custom_start_date ? classInfo.custom_start_date : classInfo.start_date)}
                      </td>
                    </tr>
                    <tr>
                      <td colSpan="2">course end:&nbsp;
                      {readableDate(!!classInfo.custom_end_date ? classInfo.custom_end_date : classInfo.end_date)}</td>
                    </tr>
                    <tr>
                      <td colSpan="2">Minimum participation requirements:
                        <ul>
                          <li>At least {classInfo.paths_per_day} paths each day</li>
                          <li>On at least {classInfo.days_per_week} different days</li>
                        </ul>
                      </td>
                    </tr>
                    <tr>
                      <td colSpan="2">I began the course at badge set {classInfo.starting_set}
                      </td>
                    </tr>
                    <tr>
                      <td colSpan="2">I will finish with an...</td>
                    </tr>
                    <tr>
                      <td>A</td>
                      <td>if I have begun badge set {Math.min(classInfo.a_cap, (classInfo.a_target + parseInt(classInfo.starting_set)))}</td>
                    </tr>
                    <tr>
                      <td>B</td>
                      <td>if I have begun badge set {Math.min(classInfo.b_cap, classInfo.b_target + parseInt(classInfo.starting_set))}</td>
                    </tr>
                    <tr>
                      <td>C</td>
                      <td>if I have begun badge set {Math.min(classInfo.c_cap, classInfo.c_target + parseInt(classInfo.starting_set))}</td>
                    </tr>
                    <tr>
                      <td>D</td>
                      <td>if I have begun badge set {Math.min(classInfo.d_cap, classInfo.d_target + parseInt(classInfo.starting_set))}</td>
                    </tr>
                    <tr>
                      <td colSpan="2">by the end of this course</td>
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
              {Array.from('x'.repeat(20), (_, i) => 1 + i).map(n => {return(
                !!badgeSetMilestones && badgeSetMilestones.find(o => o.badge_set === n) ?
                  <OverlayTrigger key={`progress-bar-set-${n}`} placement="auto" trigger="click" rootClose
                    overlay={
                      <Popover id={`tooltip-${n}`}>
                        <PopoverTitle>Badge Set {n}</PopoverTitle>
                        <PopoverContent>
                          {`Reached on ${readableDate(badgeSetMilestones.find(o => o.badge_set === n).my_date)}`}
                        </PopoverContent>
                      </Popover>
                    }
                  >
                    <div key={n} className="profile-progress-unit">{n}
                    </div>
                  </OverlayTrigger>
                :
                  <div key={n} className="profile-progress-unit">{n}
                  </div>
                )}
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
      </React.Fragment>)}
    </Row>
  )
}

export default Profile;
