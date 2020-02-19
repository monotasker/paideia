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

  return response;
}

const evaluateAnswer = async ({location=null,
                               repeat=false,
                               response_string=null,
                               pre_bug_step_id=null}) => {
  let response = await fetch('/paideia/api/evaluate_answer', {
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
        pre_bug_step_id: pre_bug_step_id
      })
  })
  return response
}

const getStepQueries = async ({step_id=null, user_id=null}) => {
  let response = await fetch('/paideia/api/get_step_queries', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        step_id: step_id,
        user_id: user_id
      })
  })
  return response
}

const submitNewQuery = async ({step_id=null,
                               path_id=null,
                               user_id=null,
                               loc_name=null,
                               answer="",
                               log_id=null,
                               score=null,
                               user_comment=null}) => {
  let response = await fetch('/paideia/api/log_new_query', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        step_id: step_id,
        path_id: path_id,
        user_id: user_id,
        loc_name: loc_name,
        answer: answer,
        log_id: log_id,
        score: score,
        user_comment: user_comment
      })
  })
  return response
}

export { getPromptData, evaluateAnswer, getStepQueries, submitNewQuery }