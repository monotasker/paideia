import React, {
  useReducer,
  createContext
} from "react";

const UserContext = createContext();
// const UserDispatchContext = createContext();

const speakerImages = [
  {label: "Ἀλεξανδρος",
   filename: "people_alexandros.png"},
  {label: "݂݂Μαρια",
   filename: "people_maria.png"},
  {label: "Στεφανος",
   filename: "people_stephanos.png"},
  {label: "Φοιβη",
   filename: "people_phoebe.png"},
  {label: "Γεωργιος",
   filename: "people_georgios.png"},
  {label: "Σοφια",
   filename: "people_sophia.png"},
]

const locationBackgrounds = [
  {label: "ἀγορά",
   filename: "bg_location_agora"},
  {label: "πανδοκειον Ἀλεξανδρου",
   filename: "bg_location_agora"},
  {label: "συναγωγη",
   filename: "bg_location_synagogue"},
  {label: "γυμνασιον",
   filename: "bg_location_gymnasion"},
  {label: "βαλανειον",
   filename: "bg_location_balaneion"},
  {label: "στοα",
   filename: "bg_location_stoa"},
]

const samplePaths = [
  {id: 1542,
   tags: '',
   steps: [
      {id: 2190,
       status: "inactive",
       type: 'text_response',
       prompt: "I may ask Maria to let you do some work in my shop. But you'll have to know how to talk with the customers. How would you ask \"What do you want?\" in Greek?",
       audio: null,
       image: null,
       evaluations: [
         {regex: "^(?P<b>Συ )?(?P<a>(τ|Τ)ί )?(?(b)|(?P<c>συ ))?(Θ|θ)ελεις(?(b)|(?(c)|(?P<d> συ)))?(?(a)| τί)(?(b)|(?(c)|(?(d)| συ)))?;$",
          score: 1.0},
         {regex: "^(?=.*(Τ|τ)ί)(?=.*(Θ|θ)ελεις).*$",
          score: 0.5}
        ],
        sampleAnswers: ["Τί θελεις;", "Θελεις τί;"],
        hints: [],
        instructions: [
          {label: "answer in Greek"},
          {label: "full clause"}
        ],
        tags: {
          primary: [
            {label: "simple transitive clauses"},
            {label: "present active indicative"},
            {label: "vocabulary - verbs of trade"},
            {label: "accusative 3"},
          ],
          secondary: [
            {label: "alphabet-basic"},
            {label: "alphabet-advanced"},
            {label: "alphabet-intermediate"},
            {label: "alphabet-final"},
            {label: "interrogative-pronoun"},
            {label: "questions1_what-who"},
          ]
        },
        tagsAhead: [],
        lemmas: [],
        npcs: [
          {name: "Ἀλεξανδρος"}
        ],
        locations: [
          {label: "ἀγορά"},
          {label: "πανδοκειον Ἀλεξανδρου"}
        ]
      }
   ]
  },
  {id: 1542,
   tags: 2190,
   steps: [
   ]
  }
]

let userDefaults = {
  userId: window.localStorage.getItem('userId') || null,
  firstName: window.localStorage.getItem('firstName') || null,
  lastName: window.localStorage.getItem('lastName') || null,
  userEmail: window.localStorage.getItem('userEmail') || null,
  userRoles: window.localStorage.getItem('userRoles') || [],
  userToken: window.localStorage.getItem('userToken') || null,
  userTimezone: window.localStorage.getItem('userTimezone') || null,
  userLoggedIn: window.localStorage.getItem('userLoggedIn') || false,
  flags: window.localStorage.getItem('flags') || [],
  currentLocation: window.localStorage.getItem('currentLocation') || null,
  currentLocationBG: window.localStorage.getItem('currentLocationBG') || null,
  currentNpc: window.localStorage.getItem('currentNpc') || null,
  currentNpcImage: window.localStorage.getItem('currentNpcImage') || null,
  currentPath: window.localStorage.getItem('currentPath') || null,
  currentStep: window.localStorage.getItem('currentStep') || null,
  completedSteps: window.localStorage.getItem('completedSteps') || [],
  completedPaths: window.localStorage.getItem('completedPaths') || [],
  availablePaths: window.localStorage.getItem('availablePaths') || [],
}


function userReducer(state, action) {
  switch (action.type) {
    case 'initializeUser': {
      window.localStorage.setItem('userId', action.payload.userId);
      window.localStorage.setItem('firstName', action.payload.firstName);
      window.localStorage.setItem('lastName', action.payload.lastName);
      window.localStorage.setItem('userEmail', action.payload.email);
      window.localStorage.setItem('userLoggedIn', true);
      return({
        ...state,
        userId: action.payload.userId,
        firstName: action.payload.firstName,
        lastName: action.payload.lastName,
        userEmail: action.payload.email,
        userLoggedIn: true,
        userRoles: [],
        userToken: '',
        userTimezone: '',
        flags: [],
        currentPath: null,
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
        currentPath: null,
      })
    }
    case 'setCurrentLoc': {
      return({
        ...state,
        currentLocation: action.payload,
        currentLocationBG: locationBackgrounds[action.payload]
      })
    }
    case 'setCurrentNpc': {
      return({
        ...state,
        currentNpc: action.payload,
        currentNpcImage: speakerImages[action.payload]
      })
    }
    case 'setPaths': {
      return {...state, availablePaths: samplePaths}
    }
    case 'setCurrentPath': {
      return {...state, currentPath: state.availablePaths[0]}
    }
    case 'setCurrentStep': {
      return {...state, currentStep: state.currentPath.steps[0]}
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
