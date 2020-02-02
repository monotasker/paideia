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
  if ( mydata.status === 200 ) {
      action(mydata);
  } else if ( mydata.status === 401 ) {
      reducer({type: 'deactivateUser', payload: null});
      history.push("/login");
  }
}

export { login, logout, checkLogin, returnStatusCheck }