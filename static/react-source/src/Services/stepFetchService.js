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
                              pre_bug_step_id=null,
                              testing=false}) => {
  return(
    doApiCall({loc: location,
               repeat: repeat,
               response_string: response_string,
               set_review: set_review,
               path: path,
               step: step,
               set_blocks: set_blocks,
               new_user: new_user,
               pre_bug_step_id: pre_bug_step_id,
               testing: testing},
              "get_prompt", "JSON", "POST")
  )
}

const set_lessons_viewed = async () => doApiCall({}, "set_viewed_slides", "none", "POST");

const evaluateAnswer = async ({location=null,
                               repeat=false,
                               response_string=null,
                               pre_bug_step_id=null}) => {
  return(
    doApiCall({loc: location, repeat: repeat,
              response_string: response_string,
              pre_bug_step_id: pre_bug_step_id},
              "evaluate_answer", "JSON", "POST")
  )
}

const fetchVocabulary = async ({vocab_scope_selector=0}
                               ) => doApiCall(
                                      {vocab_scope_selector: vocab_scope_selector},
                                      "get_vocabulary", "JSON", "POST");

const fetchLessons = async () => doApiCall({}, "get_lessons", "null", "POST");

const setServerReviewMode = async (mylevel) => doApiCall(
  {review_set: mylevel}, "set_review_mode", "JSON", "POST");

export { getPromptData,
         set_lessons_viewed,
         evaluateAnswer,
         fetchVocabulary,
         fetchLessons,
         setServerReviewMode
         }
