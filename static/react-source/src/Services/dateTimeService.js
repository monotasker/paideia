import moment from "moment";

const readableDateAndTime = myString => {
  const theDate = moment.utc(myString);
  const now = moment.utc();
  let output = "";
  if ( theDate.isSame(now, 'day') ) {
    output = theDate.local().format("[today at] h:mm a");
  } else if ( theDate.isSame(now.subtract(1, 'days'), 'day') ) {
    output = theDate.local().format("[yesterday at] h:mm a");
  } else if ( theDate.isSame(now, 'week') ) {
    output = theDate.local().format("ddd [at] h:mm a");
  } else if ( theDate.isSame(now, 'year') ) {
    output = theDate.local().format("MMM Do [at] h:mm a");
  } else if ( !!myString && myString !== "" ) {
    output = theDate.local().format("MMM Do YYYY [at] h:mm a");
  }
  return output;
}

export { readableDateAndTime }