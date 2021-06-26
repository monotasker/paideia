import React, { useState, useEffect } from "react";

import moment from "moment";
import { Spinner } from "react-bootstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

import { getCalendarMonth } from "../Services/authService";

const Calendar = ({year, month, monthData, user, dailyQuota, weeklyQuota,
                   parentUpdating}) => {
  /* Note that month is 0-indexed, but that the api call for calendar
  updates expects a 1-indexed month number. */
  const [ userID, setUserID ] = useState(user);
  const [ myYear, setMyYear ] = useState(year);
  const [ myMonth, setMyMonth ] = useState(month);
  const [ myMonthName, setMyMonthName ] = useState(moment.months(myMonth));
  const [ myMonthData, setMyMonthData ] = useState(monthData);
  const [ myDailyQuota, setMyDailyQuota ] = useState(!!dailyQuota ? dailyQuota : 20);
  const [ myWeeklyQuota, setMyWeeklyQuota ] = useState(!!weeklyQuota ? weeklyQuota : 5);
  const [ updating, setUpdating ] = useState(false);
  const [ onCurrentMonth, setOnCurrentMonth ] = useState(
    ( myYear === year && myMonth === month ) ? true : false );

  console.log(`parentUpdating ${parentUpdating}`);

  useEffect(() => {
    setMyMonthData(monthData);
  }, [monthData]);

  useEffect(() => {
    setOnCurrentMonth(( myYear === year && myMonth === month ) ? true : false);
  }, [myYear, year, month, myMonth]);

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
    } else if ( newMn > 11 ) {
      newMn = 0;
      newYr = yr + 1;
    }

    getCalendarMonth({userId: userID,
                      year: newYr,
                      month: newMn + 1})
    .then(info => {
      setMyMonth(info.month - 1);
      setMyMonthName(moment.months(info.month - 1));
      setMyYear(info.year);
      setMyMonthData(info.data);
      setUpdating(false);
    })
  }

  const weekCounts = myMonthData.map((wk) => {
    const count = wk.reduce((total, day) => {
                    total += day[1].length >= myDailyQuota ? 1 : 0;
                    return total
                 }, 0);
    const success = count >= myWeeklyQuota ? true : false;
    return([count, success])
    }
  );

  console.log(`onCurrentMonth ${onCurrentMonth}`);

  return (
    <React.Fragment>
    <div className="calendar">
      <div className="month-indicator">
        {!parentUpdating ? <a onClick={() => changeMonthAction(myYear, myMonth, "back")}> <FontAwesomeIcon icon="chevron-left" /> </a> :
         <Spinner animation="grow" />
        }
        {myMonthName} {myYear}
        {!parentUpdating ?
          <a onClick={!!onCurrentMonth ? null : () => changeMonthAction(myYear, myMonth, "ahead")}
            className={!!onCurrentMonth ? "disabled" : ""}
          >
              <FontAwesomeIcon icon="chevron-right" />
          </a> :
          <Spinner animation="grow" />
        }
      </div>
      <div className="day-of-week">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d =>
          <div key={d}>{d}</div>
        )}
        <div className="summary heading">Days on target</div>
      </div>
      <div className="date-grid">
          {(!updating && myMonthData) ? myMonthData.map((wk, index) => {
              return (
                <React.Fragment key={wk}>
                {wk.map(d =>
                  <div key={`${wk}-${d}`} className={`${isCurrentMonth(d[0])} ${d[1].length >= myDailyQuota ? "success" : ""}`}>
                      <span className="datenum">{makeDayNum(d[0])}</span>
                      <span className="countnum">
                        {d[1].length > 0 ? d[1].length : ""}
                      </span>
                  </div>
                )}
                 <div className={`summary row${index} ${weekCounts[index][1] ? "success" : "failure"}`}>
                   {weekCounts[index][0]} {weekCounts[index][1] ? <FontAwesomeIcon icon="check-circle" />
                   : <FontAwesomeIcon icon="exclamation-triangle" />}
                 </div>
                </React.Fragment>
              )
            }
          ) : <Spinner animation="grow" />}
      </div>
    </div>
    <span className="calendar-target-message">My target is at least {myDailyQuota} paths per day, {myWeeklyQuota} days per week.</span>
    </React.Fragment>
  )
}

export default Calendar;