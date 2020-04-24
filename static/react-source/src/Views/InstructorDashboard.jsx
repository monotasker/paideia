import "core-js/stable";
import "regenerator-runtime/runtime";
import React, { useState, useEffect, useContext } from "react";
import { useHistory } from "react-router-dom";

import {
  Row,
  Col,
  Form,
  Spinner,
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
    const [ activeClassId, setActiveClassId ] = useState(myClasses[0].id);
    const [ classInstitution, setClassInstitution ] = useState(myClasses[0].institution);
    const [ classYear, setClassYear ] = useState(myClasses[0].academic_year);
    const [ classTerm, setClassTerm ] = useState(myClasses[0].term);
    const [ classSection, setClassSection ] = useState(myClasses[0].course_section);
    const [ classStart, setClassStart ] = useState(
      moment(myClasses[0].start_date).toDate()
    );
    console.log(classStart);
    const [ classEnd, setClassEnd ] = useState(
      moment(myClasses[0].end_date).toDate()
    );
    console.log(classEnd);
    const [ classDailyQuota, setClassDailyQuota ] = useState(myClasses[0].paths_per_day);
    const [ classWeeklyQuota, setClassWeeklyQuota ] = useState(myClasses[0].days_per_week);
    const [ classTargetA, setClassTargetA ] = useState(myClasses[0].a_target);
    const [ classTargetB, setClassTargetB ] = useState(myClasses[0].b_target);
    const [ classTargetC, setClassTargetC ] = useState(myClasses[0].c_target);
    const [ classTargetD, setClassTargetD ] = useState(myClasses[0].d_target);
    const [ classTargetF, setClassTargetF ] = useState(myClasses[0].f_target);
    const [ classCapA, setClassCapA ] = useState(myClasses[0].a_cap);
    const [ classCapB, setClassCapB ] = useState(myClasses[0].b_cap);
    const [ classCapC, setClassCapC ] = useState(myClasses[0].c_cap);
    const [ classCapD, setClassCapD ] = useState(myClasses[0].d_cap);
    const [ classMembers, setClassMembers ] = useState([]);
    const [ classSignInLink, setClassSignInLink ] = useState(null);
    const [ classRegCode, setClassRegCode ] = useState(null);
    const [ unauthorized, setUnauthorized ] = useState(false);
    const [ missingClass, setMissingClass ] = useState(false);
    const history = useHistory();

    useEffect(() => {
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
            if ( info.hasOwnProperty(classInstitution) ) {
              setClassInstitution(info.classInstitution);
              setClassYear(info.classYear);
              setClassTerm(info.classTerm);
              setClassStart(info.classsStart);
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
      setActiveClassId(id);
    }

    return(
      <Row className="dashboard-component content-view">
        <Col className="dashboard-class-selector" xs={12} lg={4}>
          <h2>My Dashboard</h2>
          <Form.Group controlId="exampleForm.ControlSelect1">
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
        </Col>

        <Col className="dashboard-class-info" xs={12} lg={4}>
          <h3>{classSection} {classTerm} {classYear}</h3>
          <Form.Group controlId="exampleForm.ControlSelect1">
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
            />
          </Form.Group>
          <Form.Group>
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
            />
          </Form.Group>
        </Col>
      </Row>
    )
}

export default InstructorDashboard;