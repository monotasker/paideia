import React, { useState } from "react";

import moment from "moment";
import { Spinner } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { getCalendarMonth } from "../Services/authService";

const Calendar = ({year, month, monthData, user, dailyQuota, weeklyQuota}) => {
  /* Note that month is 0-indexed, but that the api call for calendar
  updates expects a 1-indexed month number. */
  const [ userID, setUserID ] = useState(user);
  const [ myYear, setMyYear ] = useState(year);
  const [ myMonth, setMyMonth ] = useState(month);
  console.log('myMonth' + myMonth.toString());
  const [ myMonthName, setMyMonthName ] = useState(moment.months(myMonth));
  const [ myMonthData, setMyMonthData ] = useState(monthData);
  const [ updating, setUpdating ] = useState(false);
  const [ onCurrentMonth, setOnCurrentMonth ] = useState(
    ( myYear === year && myMonth === month ) ? true : false );

  const makeDayNum = datestring => {
      let myString = datestring.slice(-2);
      let myInt = parseInt(myString);
      return myInt.toString();
  }

  const isCurrentMonth = datestring => {
      let myString = datestring.slice(-5, -3);
      if ( parseInt(myString) === myMonth + 1 ) {
          return "current";
      } else {
          return "";
      }
  }

  const changeMonthAction = (yr, mn, dir) => {
    setUpdating(true);
    let newYr = yr
    let newMn = (dir === "back") ? mn - 1 : mn + 1;
    if ( newMn < 0 ) {
      newMn = 11;
      newYr = yr - 1;
    } else if ( newMn > 10 ) {
      newMn = 0;
      newYr = yr + 1;
    }

    getCalendarMonth({userId: userID,
                      year: newYr,
                      month: newMn + 1})
    .then(info => {
      setMyMonth(info.calendar.month - 1);
      setMyMonthName(moment.months(info.calendar.month - 1));
      setMyYear(info.calendar.year);
      setMyMonthData(info.calendar.data);
      setUpdating(false);
    })
  }

  return (
    <div className="calendar">
      <div className="month-indicator">
        <a onClick={() => changeMonthAction(myYear, myMonth, "back")}>
          <FontAwesomeIcon icon="chevron-left" />
        </a>
        {myMonthName} {myYear}
        <a onClick={() => changeMonthAction(myYear, myMonth, "ahead")}
         className={onCurrentMonth ? "disabled" : ""}
        >
          <FontAwesomeIcon icon="chevron-right" />
        </a>
      </div>
      <div className="day-of-week">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d =>
          <div key={d}>{d}</div>
        )}
        <div className="summary">Total</div>
      </div>
      <div className="date-grid">
          {(!updating && myMonthData) ? myMonthData.map((wk, index) => {
              return (
                <React.Fragment key={wk}>
                {wk.map(d =>
                  <div key={`${wk}-${d}`} className={isCurrentMonth(d[0])}>
                      <span className="datenum">{makeDayNum(d[0])}</span>
                      <span className="countnum">{d[1].length > 0 ? d[1].length : ""}</span>
                  </div>
                )}
                <div className={`summary row${index}`}>
                  {wk.reduce((total, day) => {console.log(day[1].length); total += day[1].length; return total}, 0)}
                </div>
                </React.Fragment>
              )
            }
          ) : <Spinner animation="grow" />}
      </div>
    </div>
  )
}

export default Calendar;