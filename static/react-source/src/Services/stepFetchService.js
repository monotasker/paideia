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
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
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
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
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
  return await response.json();
}

const getGeneralQueries = async () => {

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
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const addQueryPost = async({user_id=null,
                            query_id=null,
                            post_text=null,
                            public=null,
                            prev_post=null}) => {
  let response = await fetch('/paideia/api/add_query_post', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user_id,
        query_id: query_id,
        post_text: post_text,
        public: public,
        prev_post: prev_post
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const updateQueryPost = async({user_id=null,
                               post_id=null,
                               post_text=null,
                               public=null,
                               hidden=null,
                               deleted=null,
                               flagged=null}) => {
  let response = await fetch('/paideia/api/update_query_post', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user_id,
        post_id: post_id,
        post_text: post_text,
        public: public,
        hidden: hidden,
        deleted: deleted,
        flagged: flagged
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const addQueryComment = async() => {

}

const updateQueryComment = async() => {

}

const fetchVocabulary = async ({vocab_scope_selector=0}) => {
  let response = await fetch('/paideia/api/get_vocabulary', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        vocab_scope_selector: vocab_scope_selector,
      })
  })
  return await response.json();
}

const fetchLessons = async () => {
  let response = await fetch('/paideia/api/get_lessons', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({})
  })
  return await response.json();
}


const setServerReviewMode = async (mylevel) => {
  let response = await fetch('/paideia/api/set_review_mode', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        review_set: mylevel
      })
  })
  return await response.json();
}


export { getPromptData,
         evaluateAnswer,
         getStepQueries,
         submitNewQuery,
         fetchVocabulary,
         fetchLessons,
         setServerReviewMode
         }
