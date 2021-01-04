import moment from "moment";

const readableDateAndTime = myString => {
  const theDate = moment.utc(myString);
  const now = moment.utc();
  let output = "";
  if ( theDate.isSame(now, 'day') ) {
    output = theDate.local().format("[today at] h:mma");
  } else if ( theDate.isSame(now.subtract(1, 'days'), 'day') ) {
    output = theDate.local().format("[yesterday at] h:mma");
  } else if ( theDate.isSame(now, 'week') ) {
    output = theDate.local().format("ddd [at] h:mma");
  } else if ( theDate.isSame(now, 'year') ) {
    output = theDate.local().format("MMM Do [at] h:mma");
  } else if ( !!myString && myString !== "" ) {
    output = theDate.local().format("MMM Do YYYY [at] h:mma");
  }
  return output;
}

const readableDate = myString => {
  const theDate = moment.utc(myString);
  const now = moment.utc();
  let output = "";
  if ( theDate.isSame(now, 'day') ) {
    output = theDate.local().format("[today]");
  } else if ( theDate.isSame(now.subtract(1, 'days'), 'day') ) {
    output = theDate.local().format("[yesterday]");
  } else if ( theDate.isSame(now, 'week') ) {
    output = theDate.local().format("ddd ");
  } else if ( theDate.isSame(now, 'year') ) {
    output = theDate.local().format("MMM ");
  } else if ( !!myString && myString !== "" ) {
    output = theDate.local().format("MMM Do YYYY");
  }
  return output;
}

const withinOneDay = myString => {
  const theDate = moment.utc(myString);
  const now = moment.utc();
  const dayAgo = now.subtract(1, "days");
  return theDate.isSameOrAfter(dayAgo);
}

export { readableDateAndTime,
         readableDate,
         withinOneDay
       }