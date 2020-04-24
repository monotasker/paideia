import "core-js/stable";
import "regenerator-runtime/runtime";

const login = async (formdata) => {
  let response = await fetch('/paideia/api/get_login', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })
  return await response.json()
}

const logout = async () => {
  let response = await fetch('/paideia/api/do_logout', {
      method: "GET",
      cache: "no-cache",
      mode: "same-origin"
  })
  return await response.json()
}

const checkLogin = async () => {
  let response = await fetch('/paideia/api/check_login', {
      method: "GET",
      cache: "no-cache",
      mode: "same-origin",
  })
  return await response.json()
}

const updateUserInfo = async (dispatch) => {
  let response = await fetch('/paideia/api/get_userdata', {
      method: "GET",
      cache: "no-cache",
      mode: "same-origin",
  })
  const jsonData = await response.json();
  const myinfo = formatLoginData(jsonData);
  dispatch({type: 'initializeUser', payload: myinfo});
  return myinfo
}

const getProfileInfo = async ({forSelf=false,
                               userId=null,
                               dispatch=null}) => {
  let response = await fetch('/paideia/api/get_profile_info', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user: userId,
      })
  })

  let mystatus = response.status;
  const jsonData = await response.json();
  console.log(jsonData);

  const mydata = {
    currentBadgeSet: jsonData.max_set,
    badgeLevels: jsonData.badge_levels,
    calendar: jsonData.cal,
    status_code: mystatus
  }
  if ( !!forSelf ) {
    dispatch({type: 'updateProfileInfo', payload: mydata})
  }
  return mydata
}

const getCalendarMonth = async ({userId=null,
                                 year=null,
                                 month=null}) => {
  let response = await fetch('/paideia/api/get_calendar_month', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user: userId,
        year: year,
        month: month
      })
  })

  let mystatus = response.status;
  const jsonData = await response.json();

  const mydata = {
    calendar: jsonData,
    status_code: mystatus
  }
  return mydata
}

function returnStatusCheck(mydata, history, action, reducer,
                           otherActions={}) {
  if ( mydata.status_code === 200 ) {
    action(mydata);
  } else if ( mydata.status_code === 401 ) {
    if ( mydata.reason == "Not logged in" ) {
      reducer({type: 'deactivateUser', payload: null});
      history.push("/login");
    } else if ( mydata.reason == "Insufficient privileges" ) {
      if ( otherActions.hasOwnProperty("insufficientPrivilegesAction") ) {
        otherActions.insufficientPrivilegesAction(mydata);
      }
    }
  } else if ( mydata.status_code === 404 ) {
    if ( otherActions.hasOwnProperty("noRecordAction") ) {
      otherActions.noRecordAction(mydata);
    }
  } else {
    console.log('Problem in returnStatusCheck:');
    console.log(mydata);
  }
}

const formatLoginData = (data) => {
  return {
    userId: data['id'],
    firstName: data['first_name'],
    lastName: data['last_name'],
    email: data['email'],
    userLoggedIn: true,
    userRoles: data['roles'],
    userToken: '',
    userTimezone: data['time_zone'],
    hideReadQueries: data['hide_read_queries'],
    currentBadgeSet: data['current_badge_set'],
    reviewSet: data['review_set'],
    dailyQuota: data['daily_quota'],
    weeklyQuota: data['weekly_quota'],
    classInfo: data['class_info'],
    instructing: data['instructing']
  }
}

export {
  login,
  logout,
  checkLogin,
  updateUserInfo,
  getProfileInfo,
  getCalendarMonth,
  returnStatusCheck,
  formatLoginData
}