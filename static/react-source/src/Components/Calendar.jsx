import React, { useState } from "react";

const Calendar = ({year, month, monthData, user}) => {

  const userID = useState(user);
  const myYear = useState(year);
  const myMonth = useState(month);
  const myMonthData = useState(monthData);

  return (
    <div class="calendar">
      <div class="month-indicator">
      </div>
      <div class="day-of-week">
      </div>
      <div class="date-grid">
      </div>
    </div>
  )
}

export default Calendar;