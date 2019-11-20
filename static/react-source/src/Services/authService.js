import "core-js/stable";
import "regenerator-runtime/runtime";

const login = async (formdata) => {
  let response = await fetch('/paideia/default/do_login', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })
  console.log('got fetch back');
  return response
}

const logout = async (userid) => {
  let response = await fetch('/paideia/default/do_logout', {
      method: "POST",
      cache: "no-cache",
      body: {'userid': userid}
  })
  return response
}

export { login, logout }