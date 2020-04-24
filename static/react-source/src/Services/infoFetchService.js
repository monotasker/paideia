import "core-js/stable";
import "regenerator-runtime/runtime";

const fetchClassInfo = async ({courseId=null}) => {
  let response = await fetch('/paideia/api/get_course_data', {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        course_id: courseId,
      })
  })

  let mystatus = response.status;
  const jsonData = await response.json();
  console.log(jsonData);
  if ( jsonData.hasOwnProperty("status") ) {
    const mydata = {
        status_code: mystatus,
        reason: jsonData.status
    }
    return mydata
  } else {
    const mydata = {
        classInstitution: jsonData.institution,
        classYear: jsonData.academic_year,
        classTerm: jsonData.term,
        classSection: jsonData.course_section,
        classStart: jsonData.start_date,
        classEnd: jsonData.end_date,
        classDailyQuota: jsonData.paths_per_day,
        classWeeklyQuota: jsonData.days_per_week,
        classTargetA: jsonData.a_target,
        classCapA: jsonData.a_cap,
        classTargetB: jsonData.b_target,
        classCapB: jsonData.b_cap,
        classTargetC: jsonData.c_target,
        classCapC: jsonData.c_cap,
        classTargetD: jsonData.d_target,
        classCapD: jsonData.d_cap,
        classTargetF: jsonData.f_target,
        classMembers: jsonData.members,
        status_code: mystatus
        // classSignInLink: jsonData.signin_link,
        // classRegCode: jsonData.reg_code,
    }
    return mydata
  }
}


export {
    fetchClassInfo
}