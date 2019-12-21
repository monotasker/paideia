import "core-js/stable";
import "regenerator-runtime/runtime";

const getPromptData = async ({location,
                              repeat=false,
                              response_string=null,
                              set_review=false,
                              path=null,
                              set_blocks=null,
                              new_user=false, 
                              pre_bug_step_id=null}) => {
  let payload = {}
  let response = await fetch('/paideia/api/get_prompt', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })
  return response
}

const evaluateAnswer = async () => {
  let response = await fetch('/paideia/api/get_response', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      body: formdata
  })
  return response
}

export { getPromptData, evaluateAnswer }