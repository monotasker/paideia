import React, { useState } from "react";

import moment from "moment";
import { Spinner } from "react-bootstrap";

const Calendar = ({year, month, monthData, user}) => {

  const [ userID, setUserID ] = useState(user);
  const [ myYear, setMyYear ] = useState(year);
  const [ myMonth, setMyMonth ] = useState(month);
  const [ myMonthName, setMyMonthName ] = useState(moment.months(myMonth));
  const [ myMonthData, setMyMonthData ] = useState(monthData);

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

  return (
    <div className="calendar">
      <div className="month-indicator">{myMonthName} {myYear}
      </div>
      <div className="day-of-week">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d =>
            <div key={d}>{d}</div>
          )}
      </div>
      <div className="date-grid">
          {myMonthData ? monthData.map(wk =>
              wk.map(d =>
              <div className={isCurrentMonth(d[0])}>
                  <span className="datenum">{makeDayNum(d[0])}</span>
                  <span className="countnum">{d[1].length > 0 ? d[1].length : ""}</span>
              </div>
              )
          ) : <Spinner animation="grow" />}
      </div>
    </div>
  )
}

export default Calendar;