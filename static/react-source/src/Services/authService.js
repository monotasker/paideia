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

const check_login = async () => {

}

export { login, logout, check_login }