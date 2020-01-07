import "core-js/stable";
import "regenerator-runtime/runtime";

const getPromptData = async ({location=null,
                              repeat=false,
                              response_string=null,
                              set_review=false,
                              path=null,
                              set_blocks=null,
                              new_user=false, 
                              pre_bug_step_id=null}) => {
  let response = await fetch('/paideia/api/get_prompt', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        loc: location,
        repeat: repeat,
        response_string: response_string,
        set_review: set_review,
        path: path,
        set_blocks: set_blocks,
        new_user: new_user, 
        pre_bug_step_id: pre_bug_step_id
      })
  })
  let result = null;
  if ( response.status === 200 ) {
    result = response.json();
    result['status'] = 'okay';
  } else if ( response.status === 401 ) {
    result = {'status': 'unauthorized'};
  }
  console.log('status: ' + result.status);
  return result;
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