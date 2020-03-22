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

const logout = async (userid) => {
  let response = await fetch('/paideia/api/do_logout', {
      method: "POST",
      cache: "no-cache",
      body: {'userid': userid}
  })
  return await response.json()
}

const checkLogin = async () => {
  let response = await fetch('/paideia/api/check_login', {
      method: "GET",
      cache: "no-cache"
  })
  return await response.json()
}

const updateUserInfo = async (dispatch) => {
  let response = await fetch('/paideia/api/get_userdata', {
      method: "GET",
      cache: "no-cache"
  })
  const jsonData = await response.json();
  const myinfo = formatLoginData(jsonData);
  console.log('updating local info');
  console.log(myinfo);
  dispatch({type: 'initializeUser', payload: myinfo});
  return myinfo
}

function returnStatusCheck(mydata, history, action, reducer) {
  if ( mydata.status_code === 200 ) {
    action(mydata);
  } else if ( mydata.status_code === 401 ) {
    reducer({type: 'deactivateUser', payload: null});
    history.push("/login");
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
    reviewSet: data['review_set']
  }
}

export {
  login,
  logout,
  checkLogin,
  updateUserInfo,
  returnStatusCheck,
  formatLoginData
}