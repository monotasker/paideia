import "core-js/stable";
import "regenerator-runtime/runtime";
import { doApiCall } from "../Services/utilityService";

const getPromptData = async ({location=null,
                              repeat=false,
                              response_string=null,
                              set_review=false,
                              path=null,
                              step=null,
                              set_blocks=null,
                              new_user=false,
                              pre_bug_step_id=null}) => {
    doApiCall({loc: location,
               repeat: repeat,
               response_string: response_string,
               set_review: set_review,
               path: path,
               step: step,
               set_blocks: set_blocks,
               new_user: new_user,
               pre_bug_step_id: pre_bug_step_id},
              "get_prompt", "JSON", "POST");
}

const set_lessons_viewed = async () => doApiCall({}, "set_viewed_slides", "none", "POST");

const evaluateAnswer = async ({location=null,
                               repeat=false,
                               response_string=null,
                               pre_bug_step_id=null}) => {
  doApiCall({loc: location, repeat: repeat,
             response_string: response_string,
             pre_bug_step_id: pre_bug_step_id},
             "evaluate_answer", "JSON", "POST");
}

const getQueriesMetadata = async ({user_id=0,
                                   step_id=0,
                                   nonstep=true,
                                   unanswered=false
                                  }) => {
  doApiCall({ user_id: user_id,
              step_id: step_id,
              nonstep: nonstep,
              unanswered: unanswered
            }, "get_queries_metadata", "JSON", "POST");
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
  doApiCall({step_id: step_id,
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
            },
            "get_view_queries", "JSON", "POST");
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
  doApiCall({step_id: step_id, user_id: user_id, nonstep: nonstep,
             unread: unread, unanswered: unanswered, pagesize: pagesize,
             page: page, orderby: orderby},
             "get_queries", "JSON", "POST");
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
  doApiCall({step_id: step_id,
             path_id: path_id,
             user_id: user_id,
             loc_name: loc_name,
             answer: answer=="null" ? null : answer,
             log_id: log_id,
             score: score,
             user_comment: user_comment,
             public: show_public
            },
            "log_new_query", "JSON", "POST");
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
  doApiCall({user_id: user_id,
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
            },
            "update_query", "JSON", "POST");
}

const addQueryReply = async({user_id=null,
                            query_id=null,
                            post_text=null,
                            show_public=true
                            }) => {
  doApiCall({user_id: user_id, query_id: query_id,
             post_body: post_text, public: show_public},
            "add_query_post", "JSON", "POST");
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
  doApiCall({user_id: user_id,
             post_id: post_id,
             query_id: query_id,
             post_body: post_text,
             public: show_public,
             hidden: hidden,
             deleted: deleted,
             flagged: flagged,
             pinned: pinned,
             helpfulness: helpfulness,
             popularity: popularity},
             "update_query_post", "JSON", "POST");
}

const addReplyComment = async({user_id=null,
                               post_id=null,
                               query_id=null,
                               comment_text=null,
                               show_public=null
                               }) => {
  doApiCall({user_id: user_id, bug_id: query_id, post_id: post_id,
             comment_body: comment_text, public: show_public},
             "add_post_comment", "JSON", "POST");
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
  doApiCall({user_id: user_id,
             post_id: post_id,
             comment_id: comment_id,
             comment_body: comment_text,
             public: show_public,
             hidden: hidden,
             deleted: deleted,
             flagged: flagged,
             pinned: pinned,
             helpfulness: helpfulness,
             popularity: popularity},
             "update_post_comment", "JSON", "POST");
}

const updateReadStatus = async({postLevel="",
                                userId=0,
                                postId=0,
                                readStatus=false
                              }) => {
  doApiCall({user_id: userId, post_id: postId,
             post_level: postLevel, read_status: readStatus},
             "mark_read_status", "JSON", "POST");
}

const fetchVocabulary = async ({vocab_scope_selector=0}) => {
  doApiCall({vocab_scope_selector: vocab_scope_selector},
            "get_vocabulary", "JSON", "POST");
}

const fetchLessons = async () => {
  doApiCall({}, "get_lessons", "null", "POST");}

const setServerReviewMode = async (mylevel) => {
  doApiCall({review_set: mylevel}, "set_review_mode", "JSON", "POST");}

export { getPromptData,
         set_lessons_viewed,
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
