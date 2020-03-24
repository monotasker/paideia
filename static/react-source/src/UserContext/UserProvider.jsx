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
  reviewSet: ls.getItem('reviewSet') || null,
  currentLocation: ls.getItem('currentLocation') || null,
  currentLocationBG: ls.getItem('currentLocationBG') || null,
  currentNpc: ls.getItem('currentNpc') || null,
  currentNpcImage: ls.getItem('currentNpcImage') || null,
  currentPath: ls.getItem('currentPath') || null,
  currentStep: ls.getItem('currentStep') || null,
  currentAnswer: ls.getItem('currentAnswer') || null,
  currentScore: ls.getItem('currentScore') || null,
  currentLogID: ls.getItem('currentLogID') || null,
  currentBadgeSet: ls.getItem('currentLogID') || null
}


function userReducer(state, action) {
  switch (action.type) {
    case 'initializeUser': {
      window.localStorage.setItem('userId', action.payload.userId);
      window.localStorage.setItem('firstName', action.payload.firstName);
      window.localStorage.setItem('lastName', action.payload.lastName);
      window.localStorage.setItem('userEmail', action.payload.email);
      window.localStorage.setItem('userLoggedIn', true);
      window.localStorage.setItem('userRoles', action.payload.userRoles);
      // window.localStorage.setItem('userToken', action.payload.userToken);
      window.localStorage.setItem('userTimezone', action.payload.userTimezone);
      // window.localStorage.setItem('flags', action.payload.flags);
      window.localStorage.setItem('currentPath', null);
      window.localStorage.setItem('hideReadQueries', action.payload.hideReadQueries);
      window.localStorage.setItem('currentBadgeSet', action.payload.currentBadgeSet);
      window.localStorage.setItem('reviewSet', action.payload.reviewSet);
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
        reviewSet: action.payload.reviewSet
      })
    }
    case 'deactivateUser': {
      window.localStorage.clear();
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
        reviewSet: null
      })
    }
    case 'setEvalResults': {
      console.log(action.payload);
      window.localStorage.setItem('currentAnswer', action.payload.answer);
      window.localStorage.setItem('currentScore', action.payload.score);
      window.localStorage.setItem('currentLogID', action.payload.logId);
      return({
        ...state,
        currentAnswer: action.payload.answer,
        currentScore: action.payload.score,
        currentLogID: action.payload.logId
      })
    }
    case 'setCurrentLoc': {
      window.localStorage.setItem('currentLocation', action.payload);
      return({
        ...state,
        currentLocation: action.payload
      })
    }
    case 'leaveCurrentLoc': {
      window.localStorage.setItem('currentLocation', null);
      return({
        ...state,
        currentLocation: null
      })
    }
    case 'setCurrentNpc': {
      window.localStorage.setItem('currentNpc', action.payload);
      return({
        ...state,
        currentNpc: action.payload
      })
    }
    case 'setCurrentStep': {
      window.localStorage.setItem('currentStep', action.payload.step);
      window.localStorage.setItem('currentPath', action.payload.path);
      window.localStorage.setItem('currentAnswer', null);
      window.localStorage.setItem('currentScore', null);
      window.localStorage.setItem('currentLogID', null);
      return {...state,
        currentStep: action.payload.step,
        currentPath: action.payload.path,
        currentAnswer: null,
        currentScore: null,
        currentLogID: null
      }
    }
    case 'setReviewSet': {
      window.localStorage.setItem('reviewSet', action.payload);
      return {...state,
        reviewSet: action.payload
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
