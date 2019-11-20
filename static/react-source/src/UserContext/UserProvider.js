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
  userId: null,
  firstName: null,
  lastName: null,
  userEmail: null,
  userRoles: [],
  userToken: null,
  userTimezone: null,
  userLoggedIn: false,
  flags: [],
  currentLocation: null,
  currentLocationBG: null,
  currentNpc: null,
  currentNpcImage: null,
  currentPath: null,
  currentStep: null,
  completedSteps: [],
  completedPaths: [],
  availablePaths: [],
}


function userReducer(state, action) {
  switch (action.type) {
    case 'initializeUser': {
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
  const [state, dispatch] = useReducer(userReducer, userDefaults);

  return (
    <UserContext.Provider value={{ state, dispatch }}>
      {children}
    </UserContext.Provider>
  );
}

export default UserProvider;
export { UserContext };
