import "core-js/stable";
import "regenerator-runtime/runtime";

import { doApiCall } from "../Services/utilityService";

const fetchClassInfo = async ({courseId=null}) => {
  let response = await doApiCall({course_id: courseId}, 'get_course_data', "JSON");

  let mydata;
  if ( response.hasOwnProperty("status") ) {
    mydata = response;
  } else {
    mydata = {
        classInstitution: response.institution,
        classYear: response.academic_year,
        classTerm: response.term,
        classSection: response.course_section,
        classInProcess: response.in_process,
        classStart: response.start_date,
        classEnd: response.end_date,
        classDailyQuota: response.paths_per_day,
        classWeeklyQuota: response.days_per_week,
        classTargetA: response.a_target,
        classCapA: response.a_cap,
        classTargetB: response.b_target,
        classCapB: response.b_cap,
        classTargetC: response.c_target,
        classCapC: response.c_cap,
        classTargetD: response.d_target,
        classCapD: response.d_cap,
        classTargetF: response.f_target,
        classMembers: response.members,
        status_code: response.status_code
        // classSignInLink: jsonData.signin_link,
        // classRegCode: jsonData.reg_code,
    }
    return mydata
  }
}

export {
    fetchClassInfo
}