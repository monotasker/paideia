import React, {
  useReducer,
  createContext
} from "react";

const UserContext = createContext();
// const UserDispatchContext = createContext();
const ls = window.localStorage

let userDefaults = {
  userId: parseInt(ls.getItem('userId')) || null,
  firstName: ls.getItem('firstName') || null,
  lastName: ls.getItem('lastName') || null,
  userEmail: ls.getItem('userEmail') || null,
  userRoles: !!ls.getItem('userRoles') && ls.getItem('userRoles').split(',') || [],
  userToken: ls.getItem('userToken') || null,
  userTimezone: ls.getItem('userTimezone') || null,
  userLoggedIn: ( ls.getItem('userLoggedIn') === "true" ) || false,
  flags: ls.getItem('flags') || [],
  hideReadQueries: ( ls.getItem('hideReadQueries') === "true" ) || null,
  reviewSet: parseInt(ls.getItem('reviewSet')) || null,
  currentLocation: ls.getItem('currentLocation') || null,
  currentLocationBG: ls.getItem('currentLocationBG') || null,
  currentNpc: ls.getItem('currentNpc') || null,
  currentNpcImage: ls.getItem('currentNpcImage') || null,
  currentPath: parseInt(ls.getItem('currentPath')) || null,
  currentStep: parseInt(ls.getItem('currentStep')) || null,
  currentAnswer: ls.getItem('currentAnswer') || null,
  currentScore: ls.getItem('currentScore') || null,
  currentLogID: parseInt(ls.getItem('currentLogID')) || null,
  currentBadgeSet: parseInt(ls.getItem('currentBadgeSet')) || null,
  badgeLevels: JSON.parse(ls.getItem('badgeLevels')) || null,
  calendar: JSON.parse(ls.getItem('calendar')) || null,
  dailyQuota: parseInt(ls.getItem('dailyQuota')) || null,
  weeklyQuota: parseInt(ls.getItem('weeklyQuota')) || null,
  classInfo: JSON.parse(ls.getItem('classInfo')) || null,
  instructing: JSON.parse(ls.getItem('instructing')) || null
}


function userReducer(state, action) {
  switch (action.type) {
    case 'initializeUser': {
      ls.setItem('userId', action.payload.userId);
      ls.setItem('firstName', action.payload.firstName);
      ls.setItem('lastName', action.payload.lastName);
      ls.setItem('userEmail', action.payload.email);
      ls.setItem('userLoggedIn', true);
      ls.setItem('userRoles', action.payload.userRoles);
      // ls.setItem('userToken', action.payload.userToken);
      ls.setItem('userTimezone', action.payload.userTimezone);
      // ls.setItem('flags', action.payload.flags);
      ls.setItem('currentPath', null);
      ls.setItem('hideReadQueries', action.payload.hideReadQueries);
      ls.setItem('currentBadgeSet', action.payload.currentBadgeSet);
      ls.setItem('reviewSet', action.payload.reviewSet);
      ls.setItem('dailyQuota', action.payload.dailyQuota);
      ls.setItem('weeklyQuota', action.payload.weeklyQuota);
      ls.setItem('classInfo', JSON.stringify(action.payload.classInfo));
      ls.setItem('instructing', JSON.stringify(action.payload.instructing));

      return({
        ...state,
        userId: action.payload.userId,
        firstName: action.payload.firstName,
        lastName: action.payload.lastName,
        userEmail: action.payload.email,
        userLoggedIn: true,
        userRoles: action.payload.userRoles,
        userToken: '',
        userTimezone: action.payload.userTimezone,
        flags: [],
        currentPath: null,
        hideReadQueries: action.payload.hideReadQueries,
        currentBadgeSet: action.payload.currentBadgeSet,
        reviewSet: action.payload.reviewSet,
        dailyQuota: action.payload.dailyQuota,
        weeklyQuota: action.payload.weeklyQuota,
        classInfo: action.payload.classInfo,
        instructing: action.payload.instructing
      })
    }
    case 'deactivateUser': {
      ls.clear();
      return({
        ...state,
        userId: null,
        firstName: null,
        lastName: null,
        userEmail: null,
        userLoggedIn: false,
        userRoles: [],
        userToken: '',
        userTimezone: '',
        flags: [],
        currentStep: null,
        currentPath: null,
        currentLocation: null,
        hideReadQueries: null,
        currentBadgeSet: null,
        reviewSet: null,
        dailyQuota: null,
        weeklyQuota: null,
        classInfo: null,
        instructing: null
      })
    }
    case 'setEvalResults': {
      console.log(action.payload);
      ls.setItem('currentAnswer', action.payload.answer);
      ls.setItem('currentScore', action.payload.score);
      ls.setItem('currentLogID', action.payload.logId);
      return({
        ...state,
        currentAnswer: action.payload.answer,
        currentScore: action.payload.score,
        currentLogID: action.payload.logId
      })
    }
    case 'setCurrentLoc': {
      ls.setItem('currentLocation', action.payload);
      return({
        ...state,
        currentLocation: action.payload
      })
    }
    case 'leaveCurrentLoc': {
      ls.setItem('currentLocation', null);
      return({
        ...state,
        currentLocation: null
      })
    }
    case 'setCurrentNpc': {
      ls.setItem('currentNpc', action.payload);
      return({
        ...state,
        currentNpc: action.payload
      })
    }
    case 'setCurrentStep': {
      ls.setItem('currentStep', action.payload.step);
      ls.setItem('currentPath', action.payload.path);
      ls.setItem('currentAnswer', null);
      ls.setItem('currentScore', null);
      ls.setItem('currentLogID', null);
      return {...state,
        currentStep: action.payload.step,
        currentPath: action.payload.path,
        currentAnswer: null,
        currentScore: null,
        currentLogID: null
      }
    }
    case 'setReviewSet': {
      ls.setItem('reviewSet', action.payload);
      return {...state,
        reviewSet: action.payload
      }
    }
    case 'updateProfileInfo': {
      ls.setItem('currentBadgeSet', action.payload.currentBadgeSet);
      ls.setItem('badgeLevels', JSON.stringify(action.payload.badgeLevels));
      ls.setItem('calendar', JSON.stringify(action.payload.calendar));
      return {...state,
        currentBadgeSet: action.payload.currentBadgeSet,
        badgeLevels: action.payload.badgeLevels,
        calendar: action.payload.calendar
      }
    }
    case 'updateCalendarInfo': {
      ls.setItem('calendar', action.payload.calendar);
      return {...state,
        calendar: action.payload.calendar
      }
    }
    default: {
      throw new Error(`Unhandled action type: ${action.type}`)
    }
  }
}

function UserProvider({children}) {
  const [user, dispatch] = useReducer(userReducer, userDefaults);

  return (
    <UserContext.Provider value={{ user, dispatch }}>
      {children}
    </UserContext.Provider>
  );
}

export default UserProvider;
export { UserContext };
