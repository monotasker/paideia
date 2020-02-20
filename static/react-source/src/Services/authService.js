import "core-js/stable";
import "regenerator-runtime/runtime";

const login = async (formdata) => {
  let response = await fetch('/paideia/api/get_login', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })
  return response
}

const logout = async (userid) => {
  let response = await fetch('/paideia/api/do_logout', {
      method: "POST",
      cache: "no-cache",
      body: {'userid': userid}
  })
  return response
}

const checkLogin = async () => {

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

export { login, logout, checkLogin, returnStatusCheck }