import "core-js/stable";
import "regenerator-runtime/runtime";
import React, { useState, useEffect, useContext } from "react";
import { useHistory, Link } from "react-router-dom";

import {
  Alert,
  Button,
  Col,
  Form,
  FormGroup,
  Row,
  Spinner,
  Tab,
  Table,
  Tabs
} from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import moment from "moment";
import DayPickerInput from "react-day-picker/DayPickerInput";
import { formatDate, parseDate } from "react-day-picker/moment";
import 'react-day-picker/lib/style.css';

import {UserContext} from "../UserContext/UserProvider";
import {fetchClassInfo} from "../Services/infoFetchService";
import { doApiCall, returnStatusCheck } from "../Services/utilityService";
import { urlBase } from "../variables";
import { sendFormRequest,
         useResponseCallbacks
       } from "../Services/formsService";


const InstructorDashboard = () => {

    const { user, dispatch } = useContext(UserContext);
    const myhistory = useHistory();
    const [ myClasses, setMyClasses ] = useState(!!user.instructing ?
      user.instructing.sort(
        (a, b) => (Date.parse(a.start_date) > Date.parse(b.start_date)) ? -1 : 1)
      :
      []
    );
    const [ activeClassInfo, setActiveClassInfo ] = useState(myClasses[0]);
    const [ classInProcess, setClassInProcess ] = useState();
    const [ activeClassId, setActiveClassId ] = useState(
      !!activeClassInfo ? activeClassInfo.id : 0);
    const [ classInstitution, setClassInstitution ] = useState(
      !!activeClassInfo ? activeClassInfo.institution : null);
    const [ classYear, setClassYear ] = useState(
      !!activeClassInfo ? (activeClassInfo.academic_year || '') : null);
    console.log(classYear);
    const [ classTerm, setClassTerm ] = useState(
      !!activeClassInfo ? ( activeClassInfo.term || '' ) : null);
    console.log(classTerm);
    const [ classSection, setClassSection ] = useState(
      !!activeClassInfo ? ( activeClassInfo.course_section || '' ) : null);
    const [ classStart, setClassStart ] = useState(
      !!activeClassInfo ? moment(activeClassInfo.start_date).toDate() : null);
    const [ classEnd, setClassEnd ] = useState(
      !!activeClassInfo ? moment(activeClassInfo.end_date).toDate() : null);
    const [ classDailyQuota, setClassDailyQuota ] = useState(
      !!activeClassInfo ? ( activeClassInfo.paths_per_day || '' ) : null);
    const [ classWeeklyQuota, setClassWeeklyQuota ] = useState(
      !!activeClassInfo ? ( activeClassInfo.days_per_week || '' ) : null);
    const [ classTargetA, setClassTargetA ] = useState(
      !!activeClassInfo ? ( activeClassInfo.a_target || 'set me' ) : null);
    const [ classTargetB, setClassTargetB ] = useState(
      !!activeClassInfo ? ( activeClassInfo.b_target || '' ) : null);
    const [ classTargetC, setClassTargetC ] = useState(
      !!activeClassInfo ? ( activeClassInfo.c_target || '' ) : null);
    const [ classTargetD, setClassTargetD ] = useState(
      !!activeClassInfo ? ( activeClassInfo.d_target || '' ) : null);
    const [ classTargetF, setClassTargetF ] = useState(
      !!activeClassInfo ? ( activeClassInfo.f_target || '' ) : null);
    const [ classCapA, setClassCapA ] = useState(
      !!activeClassInfo ? ( activeClassInfo.a_cap || '' ) : null);
    const [ classCapB, setClassCapB ] = useState(
      !!activeClassInfo ? ( activeClassInfo.b_cap || '' ) : null);
    const [ classCapC, setClassCapC ] = useState(
      !!activeClassInfo ? ( activeClassInfo.c_cap || '' ) : null);
    const [ classCapD, setClassCapD ] = useState(
      !!activeClassInfo ? ( activeClassInfo.d_cap || '' ) : null);
    const [ classMembers, setClassMembers ] = useState([]);
    // const [ classSignInLink, setClassSignInLink ] = useState(null);
    // const [ classRegCode, setClassRegCode ] = useState(null);
    const [ fetchingClass, setFetchingClass ] = useState(false);
    const [ fetchingStudents, setFetchingStudents ] = useState(false);
    const history = useHistory();

    // flags are unauthorized, serverError, badRequest, noRecord, success
    // callbacks are serErrorAction, unauthorizedAction,
    // badRequestAction, noRecordAction, successAction
    let {missing, setMissing,
         flags, setFlags, myCallbacks} = useResponseCallbacks();
    let {studentMissing, setStudentMissing, studentFlags,
         setStudentFlags, myStudentCallbacks} = useResponseCallbacks();

    useEffect(() => {
      console.log('fetching');
      setFetchingClass(true);

      fetchClassInfo({courseId: activeClassId})
      .then(info => {
        returnStatusCheck(info, history,
          info => {
            console.log(info);
            if ( info.hasOwnProperty("classInstitution") ) {
              setClassInProcess(info.classInProcess);
              setClassInstitution(info.classInstitution);
              setClassSection(info.classSection);
              setClassYear(info.classYear);
              setClassTerm(info.classTerm);
              setClassStart(info.classStart);
              setClassEnd(info.classEnd);
              setClassDailyQuota(info.classDailyQuota);
              setClassWeeklyQuota(info.classWeeklyQuota);
              setClassTargetA(info.classTargetA);
              setClassTargetB(info.classTargetB);
              setClassTargetC(info.classTargetC);
              setClassTargetD(info.classTargetD);
              setClassTargetF(info.classTargetF);
              setClassCapA(info.classCapA);
              setClassCapB(info.classCapB);
              setClassCapC(info.classCapC);
              setClassCapD(info.classCapD);
              setClassMembers(info.classMembers);
              myCallbacks.successAction();
              setFetchingClass(false);
            } else {
              myCallbacks.serverErrorAction();
            }
          },
          dispatch,
          {insufficientPrivilegesAction: myCallbacks.unauthorizedAction,
           noRecordAction: myCallbacks.noRecordAction
          }
        );
      });
    }, [activeClassId]);

    const changeClassAction = (id) => { setActiveClassId(id); }

    const classDataConflictAction = (data) => {};
    const studentDataConflictAction = (data) => {};

    const updateClassData = (event) => {
      event.preventDefault();
      let fieldSet = {institution: [classInstitution, setClassInstitution],
                academic_year: [classYear, setClassYear],
                term: [classTerm, setClassTerm],
                course_section: [classSection, setClassSection],
                start_date: [classStart, setClassStart],
                end_date: [ classEnd, setClassEnd ],
                paths_per_day: [ classDailyQuota, setClassDailyQuota ],
                days_per_week: [ classWeeklyQuota, setClassWeeklyQuota ],
                a_target: [ classTargetA, setClassTargetA ],
                b_target: [ classTargetB, setClassTargetB ],
                c_target: [ classTargetC, setClassTargetC ],
                d_target: [ classTargetD, setClassTargetD ],
                f_target: [ classTargetF, setClassTargetF ],
                a_cap: [ classCapA, setClassCapA ],
                b_cap: [ classCapB, setClassCapB ],
                c_cap: [ classCapC, setClassCapC ],
                d_cap: [ classCapD, setClassCapD ]
               }
      let updateData = {course_id: activeClassId,
                        course_data: {}}
      Object.keys(fieldSet).forEach((k) => {
        updateData["course_data"][k] = fieldSet[k][0];
      });

      sendFormRequest(null, {
          formId: 'dashboard-class-info-form',
          fieldSet: fieldSet,
          requestAction: () => doApiCall(updateData, "update_course_data",
                                         "form"),
          history: myhistory,
          dispatch: dispatch,
          successCallback: myCallbacks.successAction,
          otherCallbacks: {serverErrorAction: myCallbacks.serverErrorAction,
                           dataConflictAction: classDataConflictAction,
                           badRequestAction: myCallbacks.badRequestAction,
                           unauthorizedAction: myCallbacks.unauthorizedAction
                          },
          setInProgressAction: setFetchingClass
        });
    }

/**     useEffect(() => {
      console.log("handling form change");
      console.log(classStart);
      console.log(classEnd);
      console.log(classDailyQuota);
      console.log(classWeeklyQuota);
      console.log(classCapA);
      console.log(classCapB);
      console.log(classCapC);
      console.log(classCapD);
      console.log(classTargetA);
      console.log(classTargetB);
      console.log(classTargetC);
      console.log(classTargetD);
      console.log(classTargetF);
    }, [classStart, classEnd, classDailyQuota, classWeeklyQuota, classCapA, classCapB, classCapC, classCapD, classTargetA, classTargetB, classTargetC, classTargetD, classTargetF]
    )*/

    // console.log(`user? ${!!user}`);
    // console.log(`user.userLoggedIn? ${!!user.userLoggedIn}`);
    // console.log(`user has roles?`);
    // console.log(!!user.userRoles && !!["instructors", "administrators"]
    //               .some(r => user.userRoles.includes(r)));

    return(
      <Row className="dashboard-component content-view">
        <Col>
          { (!user || user.userLoggedIn !== true ) &&
              myhistory.push(`/${urlBase}/login?need_login=true`)
          }
          { ( !user.userRoles || !["instructors", "administrators"]
                  .some(r => user.userRoles.includes(r) )) ?
            <Alert variant="danger">
              <Col xs="auto">
                <FontAwesomeIcon size="2x" icon="exclamation-triangle" />
              </Col>
              <Col xs="10">
                Sorry, you have to be logged in as an instructor or administrator to enter this area.
              </Col>
            </Alert>
            :
          <React.Fragment>
          <h2>My Dashboard</h2>
          <Form.Group controlId="classForm.classSelector">
            <Form.Label>Choose a class group</Form.Label>
            <Form.Control as="select"
              onChange={e => changeClassAction(e.target.value)}
            >
              {myClasses.map((c, index) =>
                <option key={index} value={c.id}>
                  {`${c.course_section}, ${c.term}, ${c.academic_year}, ${c.institution}`}
                </option>
              )}
            </Form.Control>
          </Form.Group>

        <Tabs>
        <Tab eventKey="course-details" title="Course Details">
        <Form role="form"
          id="dashboard-class-info-form"
        >
          <Form.Row>
            <Col className="dashboard-class-info" xs={12} lg={4}>
              {!!fetchingClass && <Spinner animation="grow" variant="info" />}
              <h3>{classSection} {classTerm} {classYear}</h3>
              <Form.Group controlId="start_date">
                <Form.Label>Begins</Form.Label>
                <DayPickerInput
                  onDayChange={day => setClassStart(day)}
                  formatDate={formatDate}
                  parseDate={parseDate}
                  format="LL"
                  dayPickerProps={{
                    selectedDays: {classStart}
                  }}
                  placeholder={`${formatDate(new Date(classStart), 'LL')}`}
                  onChange={e => setClassStart(e.target.value)}
                />
              </Form.Group>
              <Form.Group controlId="end_date">
                <Form.Label>Ends</Form.Label>
                <DayPickerInput
                  onDayChange={day => setClassEnd(day)}
                  formatDate={formatDate}
                  parseDate={parseDate}
                  format="LL"
                  dayPickerProps={{
                    selectedDays: {classEnd}
                  }}
                  placeholder={`${formatDate(new Date(classEnd), 'LL')}`}
                  onChange={e => setClassStart(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col>
              <h4>Minimum Participation Requirements</h4>
              <Form.Group controlId="paths_per_day">
                <Form.Label>Minimum paths / day</Form.Label>
                <Form.Control
                  value={classDailyQuota}
                  onChange={e => setClassDailyQuota(e.target.value)}
                ></Form.Control>
              </Form.Group>
              <Form.Group controlId="days_per_week">
                <Form.Label>Minimum days / week</Form.Label>
                <Form.Control
                  value={classWeeklyQuota}
                  onChange={e => setClassWeeklyQuota(e.target.value)}
                ></Form.Control>
              </Form.Group>
            </Col>
            <Col>
              <h4>Grading Targets</h4>
              <Table>
                <thead>
                  <tr>
                    <th>Letter Grade</th>
                    <th>Personal Set Progress</th>
                    <th></th>
                    <th>Absolute Set Reached</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>A</td>
                    <td>
                      <FormGroup controlId="a_target">
                        <Form.Control value={classTargetA}
                          onChange={e => setClassTargetA(e.target.value)}
                        />
                      </FormGroup> new sets
                    </td>
                    <td>OR</td>
                    <td>

                      <FormGroup controlId="a_cap">
                        Begin set <Form.Control value={classCapA}
                          onChange={e => setClassCapA(e.target.value)}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>B</td>
                    <td>
                      <FormGroup controlId="b_target">
                        <Form.Control value={classTargetB}
                          onChange={e => setClassTargetB(e.target.value)}
                        /> new sets
                      </FormGroup>
                    </td>
                    <td>OR</td>
                    <td>
                      <FormGroup controlId="b_cap">
                        Begin set <Form.Control value={classCapB}
                          onChange={e => setClassCapB(e.target.value)}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>C</td>
                    <td>
                      <FormGroup controlId="c_target">
                        <Form.Control value={classTargetC}
                          onChange={e => setClassTargetC(e.target.value)}
                        /> new sets
                      </FormGroup>
                    </td>
                    <td>OR</td>
                    <td>
                      <FormGroup controlId="c_cap">
                        Begin set <Form.Control value={classCapC}
                          onChange={e => setClassCapC(e.target.value)}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>D</td>
                    <td>
                      <FormGroup controlId="d_target">
                        <Form.Control value={classTargetD}
                          onChange={e => setClassTargetD(e.target.value)}
                        /> new sets
                      </FormGroup>
                    </td>
                    <td>OR</td>
                    <td>
                      <FormGroup controlId="d_cap">
                        Begin set <Form.Control value={classCapD}
                          onChange={e => setClassCapD(e.target.value)}
                        />
                      </FormGroup>
                    </td>
                  </tr>
                  <tr>
                    <td>F</td>
                    <td>
                      <FormGroup controlId="f_target">
                        <Form.Control value={classTargetF}
                          onChange={e => setClassTargetF(e.target.value)}
                        /> new sets
                      </FormGroup>
                    </td>
                    <td>OR</td>
                    <td>
                      NA
                    </td>
                  </tr>
                </tbody>
              </Table>
            </Col>
          </Form.Row>
          <Button variant="primary"
              type="submit"
              onClick={updateClassData}
              disabled={!!fetchingClass ? true : false }
          >
            <FontAwesomeIcon icon="save" /> Save changes
          </Button>
        </Form>
        </Tab> {/* end of course parameters tab */}

        <Tab eventKey="course-students" title="Students">
          <Table className="course-students-table">
            <thead>
              <tr>
                <td>Family Name</td>
                <td>Given Name</td>
                <td>
                  {!!classInProcess ? "Current badge set" : "Final badge set"}
                </td>
                <td>Starting badge set</td>
                <td>Progress this course</td>
                <td>Current grade achieved</td>
              </tr>
            </thead>
            <tbody>
              {classMembers.map(m =>
              <React.Fragment key={`${m.first_name}_${m.last_name}`}>
              <tr >
                <td rowSpan="2">
                  <Link to={`/${urlBase}/profile/${m.uid}`}>
                    {m.last_name}
                  </Link>
                </td>
                <td>
                  <Link to={`/${urlBase}/profile/${m.uid}`}>
                    {m.first_name}
                  </Link>
                </td>
                <td>{!!classInProcess ? m.current_set : m.ending_set }</td>
                <td>{m.starting_set}</td>
                <td>{m.progress} badge sets</td>
                <td>{m.grade}</td>
                {/* <td>{m.custom_start}</td>
                <td>{m.custom_end}</td>
                <td>{m.starting_set}</td>
                <td>{m.ending_set}</td>
                <td>{m.custom_a_cap}</td>
                <td>{m.custom_b_cap}</td>
                <td>{m.custom_c_cap}</td>
                <td>{m.custom_d_cap}</td>
                <td>{m.final_grade}</td> */}
              </tr>
              <tr>
                {/* two cells blocked off by name */}
                <td colSpan="5">
                  <Table>
                    <thead>
                      <tr>
                        <td></td>
                        <td>Days active</td>
                        <td>Days meeting minimum</td>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>This week</td>
                        <td>{m.counts[0]}</td>
                        <td>{m.counts[1]}</td>
                      </tr>
                      <tr>
                        <td>Last week</td>
                        <td>{m.counts[2]}</td>
                        <td>{m.counts[3]}</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Table>
                    <tbody>
                      <tr>
                        <td>Individual start date</td>
                        <td>{m.custom_start}</td>
                      </tr>
                      <tr>
                        <td>Individual end date</td>
                        <td>{m.custom_end}</td>
                      </tr>
                    </tbody>
                  </Table>
                  <Table>
                    <thead>
                      <tr>
                        <td>Individual grade caps</td>
                      </tr>
                      <tr>
                        <td>A</td>
                        <td>B</td>
                        <td>C</td>
                        <td>D</td>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>{m.custom_a_cap}</td>
                        <td>{m.custom_a_cap}</td>
                        <td>{m.custom_c_cap}</td>
                        <td>{m.custom_d_cap}</td>
                      </tr>
                    </tbody>
                  </Table>
                </td>
              </tr>
              </React.Fragment>
              )}
            </tbody>
          </Table>
        </Tab>
        </Tabs>
        </React.Fragment>
        }
        </Col>
      </Row>
    )
}

export default InstructorDashboard;