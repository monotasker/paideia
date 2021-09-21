import "core-js/stable";
import "regenerator-runtime/runtime";

const getPromptData = async ({location=null,
                              repeat=false,
                              response_string=null,
                              set_review=false,
                              path=null,
                              step=null,
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
        step: step,
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

const getQueriesMetadata = async ({user_id=0,
                                   step_id=0,
                                   nonstep=true,
                                   unanswered=false
                                  }) => {
  let response = await fetch('/paideia/api/get_queries_metadata', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user_id,
        step_id: step_id,
        nonstep: nonstep,
        unanswered: unanswered
      })
  })
  return await response.json();
}

const getViewQueries = async ({step_id=0,
                           user_id=0,
                           nonstep=true,
                           unread=false,
                           unanswered=false,
                           pagesize=50,
                           page=0,
                           orderby="modified_on",
                           classmates_course=0,
                           students_course=0,
                           own_queries=false
                          }) => {
  let response = await fetch('/paideia/api/get_view_queries', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        step_id: step_id,
        user_id: user_id,
        nonstep: nonstep,
        unread: unread,
        unanswered: unanswered,
        pagesize: pagesize,
        page: page,
        orderby: orderby,
        classmates_course: classmates_course,
        students_course: students_course,
        own_queries: own_queries
      })
  })
  return await response.json();
}


const getQueries = async ({step_id=null,
                           user_id=null,
                           nonstep=true,
                           unread=false,
                           unanswered=false,
                           pagesize=50,
                           page=0,
                           orderby="modified_on"
                          }) => {
  let response = await fetch('/paideia/api/get_queries', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        step_id: step_id,
        user_id: user_id,
        nonstep: nonstep,
        unread: unread,
        unanswered: unanswered,
        pagesize: pagesize,
        page: page,
        orderby: orderby
      })
  })
  return await response.json();
}

const addQuery = async ({step_id=null,
                               path_id=null,
                               user_id=null,
                               loc_name=null,
                               answer="",
                               log_id=null,
                               score=null,
                               user_comment=null,
                               show_public=true}) => {
  console.log('in service-----------------');
  console.log(show_public);
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
        answer: answer=="null" ? null : answer,
        log_id: log_id,
        score: score,
        user_comment: user_comment,
        public: show_public
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const updateQuery = async({user_id=null,
                           query_id=null,
                           query_text=null,
                           show_public=null,
                          //  hidden=null,
                           deleted=null,
                           flagged=null,
                           pinned=null,
                           helpfulness=null,
                           popularity=null,
                           score=null,
                           queryStatus=null,
                          }) => {
  let response = await fetch('/paideia/api/update_query', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user_id,
        query_id: query_id,
        user_comment: query_text,
        public: show_public,
        // hidden: hidden,
        deleted: deleted,
        flagged: flagged,
        pinned: pinned,
        helpfulness: helpfulness,
        popularity: popularity,
        score: score,
        bug_status: queryStatus
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const addQueryReply = async({user_id=null,
                            query_id=null,
                            post_text=null,
                            show_public=true
                            }) => {
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
        post_body: post_text,
        public: show_public,
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const updateQueryReply = async({user_id=null,
                               post_id=null,
                               query_id=null,
                               post_text=null,
                               show_public=null,
                               hidden=null,
                               deleted=null,
                               flagged=null,
                               pinned=null,
                               helpfulness=null,
                               popularity=null
                              }) => {
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
        query_id: query_id,
        post_body: post_text,
        public: show_public,
        hidden: hidden,
        deleted: deleted,
        flagged: flagged,
        pinned: pinned,
        helpfulness: helpfulness,
        popularity: popularity
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const addReplyComment = async({user_id=null,
                               post_id=null,
                               query_id=null,
                               comment_text=null,
                               show_public=null
                               }) => {
  let response = await fetch('/paideia/api/add_post_comment', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user_id,
        bug_id: query_id,
        post_id: post_id,
        comment_body: comment_text,
        public: show_public,
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json
}

const updateReplyComment = async({user_id=null,
                               post_id=null,
                               comment_id=null,
                               comment_text=null,
                               show_public=null,
                               hidden=null,
                               deleted=null,
                               flagged=null,
                               pinned=null,
                               helpfulness=null,
                               popularity=null
                              }) => {
  let response = await fetch('/paideia/api/update_post_comment', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: user_id,
        post_id: post_id,
        comment_id: comment_id,
        comment_body: comment_text,
        public: show_public,
        hidden: hidden,
        deleted: deleted,
        flagged: flagged,
        pinned: pinned,
        helpfulness: helpfulness,
        popularity: popularity
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json;
}

const updateReadStatus = async({postLevel="",
                                userId=0,
                                postId=0,
                                readStatus=false
                              }) => {
  let response = await fetch('/paideia/api/mark_read_status', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        post_id: postId,
        post_level: postLevel,
        read_status: readStatus
      })
  })
  let mystatus = response.status;
  let response_json = await response.json();
  response_json.status_code = mystatus;
  return response_json;
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
         getQueriesMetadata,
         getQueries,
         getViewQueries,
         addQuery,
         updateQuery,
         addQueryReply,
         updateQueryReply,
         addReplyComment,
         updateReplyComment,
         updateReadStatus,
         fetchVocabulary,
         fetchLessons,
         setServerReviewMode
         }
