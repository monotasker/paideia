
const login = async (formdata) => {
  let response = await fetch('/paideia/api/do_login', {
      method: "POST",
      cache: "no-cache",
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

export { login, logout }