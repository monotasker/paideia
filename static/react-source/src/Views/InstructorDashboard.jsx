import "core-js/stable";
import "regenerator-runtime/runtime";
import React, { useState, useEffect, useContext } from "react";
import { useHistory } from "react-router-dom";

import {
  Col,
  Form,
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
import { returnStatusCheck } from "../Services/authService";


const InstructorDashboard = () => {

    const { user, dispatch } = useContext(UserContext);
    const [ myClasses, setMyClasses ] = useState(user.instructing.sort(
        (a, b) => (Date.parse(a.start_date) > Date.parse(b.start_date)) ? -1 : 1)
    );
    const [ activeClassInfo, setActiveClassInfo ] = useState(myClasses[0]);
    const [ activeClassId, setActiveClassId ] = useState(activeClassInfo.id);
    const [ classInstitution, setClassInstitution ] = useState(activeClassInfo.institution);
    const [ classYear, setClassYear ] = useState(activeClassInfo.academic_year || '');
    console.log(classYear);
    const [ classTerm, setClassTerm ] = useState(activeClassInfo.term || '');
    console.log(classTerm);
    const [ classSection, setClassSection ] = useState(activeClassInfo.course_section || '');
    const [ classStart, setClassStart ] = useState(
      moment(activeClassInfo.start_date).toDate()
    );
    const [ classEnd, setClassEnd ] = useState(
      moment(activeClassInfo.end_date).toDate()
    );
    const [ classDailyQuota, setClassDailyQuota ] = useState(activeClassInfo.paths_per_day || '');
    const [ classWeeklyQuota, setClassWeeklyQuota ] = useState(activeClassInfo.days_per_week || '');
    const [ classTargetA, setClassTargetA ] = useState(activeClassInfo.a_target || 'set me');
    const [ classTargetB, setClassTargetB ] = useState(activeClassInfo.b_target || '');
    const [ classTargetC, setClassTargetC ] = useState(activeClassInfo.c_target || '');
    const [ classTargetD, setClassTargetD ] = useState(activeClassInfo.d_target || '');
    const [ classTargetF, setClassTargetF ] = useState(activeClassInfo.f_target || '');
    const [ classCapA, setClassCapA ] = useState(activeClassInfo.a_cap || '');
    const [ classCapB, setClassCapB ] = useState(activeClassInfo.b_cap || '');
    const [ classCapC, setClassCapC ] = useState(activeClassInfo.c_cap || '');
    const [ classCapD, setClassCapD ] = useState(activeClassInfo.d_cap || '');
    const [ classMembers, setClassMembers ] = useState([]);
    const [ classSignInLink, setClassSignInLink ] = useState(null);
    const [ classRegCode, setClassRegCode ] = useState(null);
    const [ unauthorized, setUnauthorized ] = useState(false);
    const [ missingClass, setMissingClass ] = useState(false);
    const [ fetching, setFetching ] = useState(false);
    const history = useHistory();



    useEffect(() => {
      console.log('fetching');
      setFetching(true);
      const insufficientPrivilegesAction = data => {
        setUnauthorized(true);
        console.log(data);
      }
      const noRecordAction = data => {
        setMissingClass(true);
        console.log(data);
      }

      fetchClassInfo({courseId: activeClassId})
      .then(info => {
        returnStatusCheck(info, history,
          info => {
            console.log(info);
            if ( info.hasOwnProperty("classInstitution") ) {
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
              setUnauthorized(false);
              setMissingClass(false);
              setFetching(false);
            } else if (info.reason == "Insufficient privileges") {
              setUnauthorized(true);
            } else if (info.reason == "No such record") {
              setMissingClass(true);
            }
          },
          dispatch,
          {insufficientPrivilegesAction: insufficientPrivilegesAction,
          noRecordAction: noRecordAction
          }
        );
      });
    }, [activeClassId]);

    const changeClassAction = (id) => {
      console.log('changed');
      setActiveClassId(id);
    }

    useEffect(() => {
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

    )

    return(
      <Row className="dashboard-component content-view">
        <Col>
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
        <Form>
          <Form.Row>
            <Col className="dashboard-class-info" xs={12} lg={4}>
              {!!fetching && <Spinner animation="grow" variant="info" />}
              <h3>{classSection} {classTerm} {classYear}</h3>
              <Form.Group controlId="classForm.StartDatePicker">
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
              <Form.Group controlId="classForm.endDatePicker">
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
              <Form.Group controlId="classForm.dailyQuotaInput">
                <Form.Label>Minimum paths / day</Form.Label>
                <Form.Control
                  value={classDailyQuota}
                  onChange={e => setClassDailyQuota(e.target.value)}
                ></Form.Control>
              </Form.Group>
              <Form.Group controlId="classForm.weeklyQuotaInput">
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
                      <Form.Control value={classTargetA}
                        onChange={e => setClassTargetA(e.target.value)}
                      ></Form.Control> new sets
                    </td>
                    <td>OR</td>
                    <td>
                      Begin set <Form.Control value={classCapA}
                        onChange={e => setClassCapA(e.target.value)}
                      ></Form.Control>
                    </td>
                  </tr>
                  <tr>
                    <td>B</td>
                    <td>
                      <Form.Control value={classTargetB}
                        onChange={e => setClassTargetB(e.target.value)}
                      ></Form.Control> new sets
                    </td>
                    <td>OR</td>
                    <td>
                      Begin set <Form.Control value={classCapB}
                        onChange={e => setClassCapB(e.target.value)}
                      ></Form.Control>
                    </td>
                  </tr>
                  <tr>
                    <td>C</td>
                    <td>
                      <Form.Control value={classTargetC}
                        onChange={e => setClassTargetC(e.target.value)}
                      ></Form.Control> new sets
                    </td>
                    <td>OR</td>
                    <td>
                      Begin set <Form.Control value={classCapC}
                        onChange={e => setClassCapC(e.target.value)}
                      ></Form.Control>
                    </td>
                  </tr>
                  <tr>
                    <td>D</td>
                    <td>
                      <Form.Control value={classTargetD}
                        onChange={e => setClassTargetD(e.target.value)}
                      ></Form.Control> new sets
                    </td>
                    <td>OR</td>
                    <td>
                      Begin set <Form.Control value={classCapD}
                        onChange={e => setClassCapD(e.target.value)}
                      ></Form.Control>
                    </td>
                  </tr>
                  <tr>
                    <td>F</td>
                    <td>
                      <Form.Control value={classTargetF}
                        onChange={e => setClassTargetF(e.target.value)}
                      ></Form.Control> new sets
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
        </Form>
        </Tab> {/* end of course parameters tab */}

        <Tab eventKey="course-students" title="Students">
          <Table>
            <thead>
              <tr>
                <td>Given Name</td>
                <td>Family Name</td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
              </tr>
            </thead>
            <tbody>
              {classMembers.map(m =>
              <tr>
                <td>{m.first_name}</td>
                <td>{m.last_name}</td>
                <td>{m.custom_start}</td>
                <td>{m.custom_end}</td>
                <td>{m.starting_set}</td>
                <td>{m.ending_set}</td>
                <td>{m.custom_a_cap}</td>
                <td>{m.custom_b_cap}</td>
                <td>{m.custom_c_cap}</td>
                <td>{m.custom_d_cap}</td>
                <td>{m.final_grade}</td>
              </tr>
              )}
            </tbody>
          </Table>
        </Tab>
        </Tabs>

        </Col>
      </Row>
    )
}

export default InstructorDashboard;