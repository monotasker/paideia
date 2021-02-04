import React, { useEffect } from 'react';
import "core-js/stable";
import "regenerator-runtime/runtime";
import { recaptchaKey } from "../variables";
import { loadScriptByURL } from "../Services/utilityService";

const startPasswordReset = async ({email,
                                   token,
                                  }) => {
  console.log(`email: ${email}`);
  let formdata = new FormData();
  formdata.append("email", email);
  formdata.append("token", token);

  let response = await fetch('/paideia/api/start_password_reset', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })

  let mystatus = response.status;
  const jsonData = await response.json();
  let mydata = jsonData;
  mydata.status_code = mystatus;
  return mydata;
}

const doPasswordReset = async ({resetKey,
                                token,
                                passwordA,
                                passwordB
                                }) => {
  let formdata = new FormData();
  formdata.append("key", resetKey);
  formdata.append("token", token);
  formdata.append("new_password_A", passwordA);
  formdata.append("new_password_B", passwordB);

  let response = await fetch('/paideia/api/do_password_reset', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })

  let mystatus = response.status;
  let mydata;
  try {
    mydata = await response.json();
  } catch(err) {
    mydata = {status: "internal server error",
              reason: "Unknown error in function do_password_reset",
              error: err.message}
  }
  mydata.status_code = mystatus;
  return mydata;
}

const register = async ({token,
                         firstName,
                         lastName,
                         timeZone,
                         email,
                         password
                         }) => {
  let formdata = new FormData();
  formdata.append("my_first_name", firstName);
  formdata.append("my_last_name", lastName);
  formdata.append("my_time_zone", timeZone);
  formdata.append("my_email", email);
  formdata.append("my_password", password);
  formdata.append("my_token", token);

  let response = await fetch('/paideia/api/get_registration', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })

  let mystatus = response.status;
  const jsonData = await response.json();
  let mydata = jsonData;
  mydata.status_code = mystatus;
  return mydata;
}

const login = async ({token, email, password}) => {
  let formdata = new FormData();
  formdata.append("email", email);
  formdata.append("password", password);
  formdata.append("token", token);
  let response = await fetch('/paideia/api/get_login', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })
  let mystatus = response.status;
  const jsonData = await response.json();
  let mydata = jsonData;
  mydata.status_code = mystatus;
  return mydata;
}

const logout = async () => {
  let response = await fetch('/paideia/api/do_logout', {
      method: "GET",
      cache: "no-cache",
      mode: "same-origin"
  })
  let mystatus = response.status;
  const jsonData = await response.json();
  let mydata = jsonData;
  mydata.status_code = mystatus;
  return mydata;
}

const checkLogin = async (user, dispatch) => {
  let response = await fetch('/paideia/api/check_login', {
      method: "GET",
      cache: "no-cache",
      mode: "same-origin",
  });
  const jsonData = await response.json();

  console.log('=========================================');
  console.log('CHECKING LOGIN');
  let myVal = true;

  if ( !!user.userLoggedIn && !!jsonData.logged_in ) {
    console.log('logged in both');

    if ( user.userId != jsonData.user ) {
      myVal = false;
      throw new Error("local user doesn't match server login");
    }
  } else if ( !user.userLoggedIn && !!jsonData.logged_in ) {
    console.log('logged in server only');
    updateUserInfo(dispatch);

  } else if ( (!!user.userID || !!user.userLoggedIn) && !jsonData.logged_in ) {
    console.log('logged in local only');
    dispatch({type: 'deactivateUser'});
    myVal = false;
  }
  return myVal;
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
        userId: userId,
      })
  })

  let mystatus = response.status;
  const jsonData = await response.json();
  let mydata = jsonData;
  mydata.status_code = mystatus;

  if ( mystatus===200 ) {
    mydata = {
      firstName: jsonData.the_name.first_name,
      lastName: jsonData.the_name.last_name,
      email: jsonData.email,
      timezone: jsonData.tz,
      pathsPerDay: jsonData.paths_per_day,
      daysPerWeek: jsonData.days_per_week,
      currentBadgeSet: jsonData.max_set,
      badgeLevels: jsonData.badge_levels,
      calendar: jsonData.cal,
      badgeTableData: jsonData.badge_table_data,
      answerCounts: jsonData.answer_counts,
      badgeSetDict: jsonData.badge_set_dict,
      badgeSetMilestones: jsonData.badge_set_milestones,
      chart1Data: jsonData.chart1_data,
      endDate: jsonData.end_date,
      startingSet: jsonData.starting_set,
      classInfo: jsonData.class_info,
      status_code: mystatus
    }
    if ( !!forSelf ) {
      dispatch({type: 'updateProfileInfo', payload: mydata})
    }
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
        user_id: userId,
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
  } else if ( mydata.status_code === 400 ) {
    console.log('400: Bad request');
    if ( otherActions.hasOwnProperty("badRequestAction") ) {
      otherActions.badRequestAction(mydata);
    }
  } else if ( mydata.status_code === 401 ) {
    if ( mydata.reason === "Not logged in" ) {
      console.log('401: Not logged in');
      if ( otherActions.hasOwnProperty("unauthorizedAction")) {
        otherActions.unauthorizedAction(mydata);
      } else {
        reducer({type: 'deactivateUser', payload: null});
        history.push(`login`);
      }
    } else if ( mydata.reason === "Insufficient privileges" ) {
      console.log('401: Insufficient privileges');
      if ( otherActions.hasOwnProperty("insufficientPrivilegesAction") ) {
        otherActions.insufficientPrivilegesAction(mydata);
      }
    } else if ( mydata.reason === "Login failed" ) {
      console.log('401: Login failed');
      otherActions.unauthorizedAction(mydata);
    } else if ( mydata.reason === "Action blocked") {
      console.log('401: Action blocked');
      otherActions.actionBlockedAction(mydata);
    }
  } else if ( mydata.status_code === 404 ) {
    console.log('404: No such record');
    if ( otherActions.hasOwnProperty("noRecordAction") ) {
      otherActions.noRecordAction(mydata);
    }
  } else if ( mydata.status_code === 409 ) {
    console.log('409: Conflict');
    if ( otherActions.hasOwnProperty("dataConflictAction") ) {
      console.log('taking conflict action');
      otherActions.dataConflictAction(mydata);
    }
  } else if ( mydata.status_code === 500 ) {
    console.log('500: Internal server error');
    if ( otherActions.hasOwnProperty("serverErrorAction") ) {
      otherActions.serverErrorAction(mydata);
    }
  } else {
    console.log('Uncaught problem in returnStatusCheck:');
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

/**
 * React HOC that provides recaptcha integration to the wrapped component
 *
 * The wrapped component is provided with a `submitAction` prop.
 * Any call to a server action wrapped with submitAction() will be
 * protected by recaptcha v3 and will receive the extra `token` argument
 * to pass on to the server call.
 *
 *
 * @component
 * @param {JSX.Element} Component the component to be decorated
 * @param {object} props this component's properties
 * @param {string} props.rkey a valid recaptcha v. 3 site key
 * @param {function} props.actionName a function making a server request that
 *                                    will be protected by recaptcha
 * @returns {JSX.Element} A react component with an extra `submitAction`
 *                        prop
 */
const withRecaptcha = (Component, actionName) => ({rkey=recaptchaKey,
                                                   ...throughProps}) => {
  useEffect(() => {
    loadScriptByURL("recaptcha-key",
        `https://www.google.com/recaptcha/api.js?render=${rkey}`, function () {
            console.log("Recaptcha Script loaded!");
        }
    );
  }, []);

  const submitAction = (event, myAction) => {
    event.preventDefault();
    window.grecaptcha.ready(() => {
        window.grecaptcha.execute(rkey, { action: actionName })
        .then(token => { myAction(token); });
    });
  }

  return (
    <Component submitAction={submitAction} {...throughProps} />
  )
}

const useRecaptcha = (actionName, requestFunction) => {
  console.log(actionName);
  console.log(requestFunction);
  const rkey = recaptchaKey
  useEffect(() => {
    loadScriptByURL("recaptcha-key",
        `https://www.google.com/recaptcha/api.js?render=${rkey}`, function () {
            console.log("Recaptcha Script loaded!");
        }
    );
  }, []);

  return () => {
    window.grecaptcha.ready(() => {
        window.grecaptcha.execute(rkey, { action: actionName })
        .then(token => { requestFunction(token); });
    });
  }
}

export {
  startPasswordReset,
  doPasswordReset,
  register,
  login,
  logout,
  checkLogin,
  updateUserInfo,
  getProfileInfo,
  getCalendarMonth,
  returnStatusCheck,
  formatLoginData,
  useRecaptcha,
  withRecaptcha
}