import React, { useContext, useState } from "react";
import {
    TransitionGroup,
    CSSTransition
} from "react-transition-group";
import {
    Button,
    Col,
    Form,
    Row,
    Table
} from "react-bootstrap";
import { useHistory, Link } from "react-router-dom";
import UserProvider, { UserContext } from "../UserContext/UserProvider";
import { urlBase } from "../variables";


const DativeUses = ({navigateAwayHandler}) => (
    <>
    </>
);

const PersonalEndings = ({navigateAwayHandler}) => (
    <>
    </>
);

const KindsOf3rdDeclension = ({navigateAwayHandler}) => (
    <>
    </>
);

const Common2ndAorists = ({navigateAwayHandler}) => (
    <>
    </>
);

const GenitiveUses = ({navigateAwayHandler}) => (
    <>
        <Table className="genitive-uses-table" size="sm">
            <thead>
                <tr>
                    <th colSpan="3">Common Uses of the Genitive</th>
                </tr>
                <tr>
                    <th colSpan="3"><small>L = lead nominal, G = genitive nominal</small></th>
                </tr>
                <tr>
                    <th>Genitive of...</th>
                    <th>Kind of relationship</th>
                    <th>Translation tip</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Relationship</td>
                    <td>L has a personal relationship with G</td>
                    <td>use English possessive</td>
                </tr>
                <tr>
                    <td>Possession</td>
                    <td>L is owned or possessed by G</td>
                    <td>use English possessive</td>
                </tr>
                <tr>
                    <td>Attribution</td>
                    <td>L has the quality of G</td>
                    <td>make G an English adjective</td>
                </tr>
                <tr>
                    <td>Content</td>
                    <td>G is the content of L</td>
                    <td>"full of" or "filled with"</td>
                </tr>
                <tr>
                    <td>Material</td>
                    <td>L is made out of G</td>
                    <td>"made from" or "made with"</td>
                </tr>
                <tr>
                    <td>Epexegetical</td>
                    <td>G is another word/phrase for L</td>
                    <td>"that is"</td>
                </tr>
                <tr>
                    <td>Source</td>
                    <td>L comes from G</td>
                    <td>"from"</td>
                </tr>
                <tr>
                    <td>Partitive</td>
                    <td>L is a part of G</td>
                    <td>"of" or "part of"</td>
                </tr>
            </tbody>
        </Table>
        <p>The uses of the genitive are introduced in <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/51`)}>lesson 5.1, "The Genitive Case"</Button></p>
    </>

);

const CaseEndings = ({navigateAwayHandler}) => (
    <React.Fragment>
        <Table className="case-endings-table" size="sm">
            <thead>
                <tr>
                    <th className="spacer"></th>
                    <th colSpan="6">Basic Case Endings</th>
                </tr>
                <tr>
                    <th className="spacer"></th>
                    <th colSpan="3">1st/2nd declension</th>
                    <th className="spacer"></th>
                    <th colSpan="2">3rd declension</th>
                </tr>
                <tr>
                    <th className="spacer"></th>
                    <th>masc</th>
                    <th>fem</th>
                    <th>neut</th>
                    <th className="spacer"></th>
                    <th>masc/fem</th>
                    <th>neut</th>
                </tr>
            </thead>
            <tbody>
            <tr>
                <th>nom sing</th>
                <td>ς/-</td>
                <td>-</td>
                <td>ν</td>
                <td className="spacer"></td>
                <td>ς</td>
                <td>-</td>
            </tr>
            <tr>
                <th>gen sing</th>
                <td>υ</td>
                <td>ς</td>
                <td>υ</td>
                <td className="spacer"></td>
                <td>ος</td>
                <td>ος</td>
            </tr>
            <tr>
                <th>dat sing</th>
                <td>ι</td>
                <td>ι</td>
                <td>ι</td>
                <td className="spacer"></td>
                <td>ι</td>
                <td>ι</td>
            </tr>
            <tr>
                <th>acc sing</th>
                <td>ν</td>
                <td>ν</td>
                <td>ν</td>
                <td className="spacer"></td>
                <td>α/ν</td>
                <td>-</td>
            </tr>
            <tr>
                <th>voc sing</th>
                <td>ε</td>
                <td>-</td>
                <td>ν</td>
                <td className="spacer"></td>
                <td>-</td>
                <td>-</td>
            </tr>
            <tr>
                <td colSpan="7" className="spacer"></td>
            </tr>
            <tr>
                <th>nom plur</th>
                <td>ι</td>
                <td>ι</td>
                <td>α</td>
                <td className="spacer"></td>
                <td>ες</td>
                <td>α</td>
            </tr>
            <tr>
                <th>gen plur</th>
                <td>ων</td>
                <td>ων</td>
                <td>ων</td>
                <td className="spacer"></td>
                <td>ων</td>
                <td>ων</td>
            </tr>
            <tr>
                <th>dat plur</th>
                <td>ις</td>
                <td>ις</td>
                <td>ις</td>
                <td className="spacer"></td>
                <td>σι(ν)</td>
                <td>σι(ν)</td>
            </tr>
            <tr>
                <th>acc plur</th>
                <td>υς</td>
                <td>ς</td>
                <td>α</td>
                <td className="spacer"></td>
                <td>ας</td>
                <td>α</td>
            </tr>
            <tr>
                <th>voc plur</th>
                <td>ι</td>
                <td>ι</td>
                <td>α</td>
                <td className="spacer"></td>
                <td>ες</td>
                <td>α</td>
            </tr>
            </tbody>
        </Table>
        <p>The full set of case endings is introduced for the first time in <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/81`)}>lesson 8.1, "The Dative Case"</Button></p>
    </React.Fragment>
)

const SquareOfStops = ({navigateAwayHandler}) => (
    <React.Fragment>
        <Table className="square-of-stops-table">
            <thead>
                <tr>
                    <th colSpan="6">Kinds of Stops</th>
                </tr>
                <tr>
                    <th className="spacer"></th>
                    <th>Unvoiced</th>
                    <th>Voiced</th>
                    <th>Unvoiced Fricative</th>
                    <th className="spacer"></th>
                    <th>Combined with σ</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th>Labial</th>
                    <td>π</td>
                    <td>β</td>
                    <td>φ</td>
                    <td className="spacer"></td>
                    <td>ψ</td>
                </tr>
                <tr>
                    <th>Velar</th>
                    <td>κ</td>
                    <td>γ</td>
                    <td>χ</td>
                    <td className="spacer"></td>
                    <td>ξ</td>
                </tr>
                <tr>
                    <th>Dental</th>
                    <td>τ</td>
                    <td>δ [ζ]</td>
                    <td>θ</td>
                    <td className="spacer"></td>
                    <td>σ</td>
                </tr>
            </tbody>
        </Table>
        <p>Discussed in <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/101`)}>lesson 10.1, "The Aorist Tense"</Button></p>
    </React.Fragment>
)

const VowelContractions = ({navigateAwayHandler}) => {
    return (
        <React.Fragment>
            <Table className="vowel-contractions-tableA" size="sm">
                <thead>
                    <tr>
                        <th colSpan="4">Short Vowel Combinations</th>
                    </tr>
                    <tr>
                        <th className="spacer"></th>
                        <th>α</th>
                        <th>ε</th>
                        <th>ο</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>α</th>
                        <td>α</td>
                        <td>α</td>
                        <td>ω</td>
                    </tr>
                    <tr>
                        <th>ε</th>
                        <td>η</td>
                        <td>ει</td>
                        <td>ου</td>
                    </tr>
                    <tr>
                        <th>ο</th>
                        <td>ω</td>
                        <td>ου</td>
                        <td>ου</td>
                    </tr>
                </tbody>
            </Table>
            <Table className="vowel-contractions-tableB" size="sm">
                <thead>
                    <tr>
                        <th colSpan="4">With Long Vowels/Diphthongs</th>
                    </tr>
                    <tr>
                        <th className="spacer"></th>
                        <th>ω</th>
                        <th>ου</th>
                        <th>ει</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>α</th>
                        <td>ω</td>
                        <td>ω</td>
                        <td>ᾳ</td>
                    </tr>
                    <tr>
                        <th>ε</th>
                        <td>ω</td>
                        <td>ου</td>
                        <td>ει</td>
                    </tr>
                    <tr>
                        <th>ο</th>
                        <td>ω</td>
                        <td>ου</td>
                        <td>οι</td>
                    </tr>
                </tbody>
            </Table>
            <p>
                Discussed in <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/52`)}>lesson 5.2, "The Real Stems of 3rd Declension Nouns"</Button> and in <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/73`)}>lesson 7.3, "Contract Verbs"</Button>
            </p>
        </React.Fragment>
    )
}

const ReferenceView = ({navigateAwayHandler}) => {

    const [ user, ] = useContext(UserContext);
    const userLevel = null;
    console.log("user is");
    console.log(user);
    const sections = {
        'general': [{label: 'square of stops', userLevel: {userLevel},
                    component: <SquareOfStops navigateAwayHandler={navigateAwayHandler} />},
                    {label: 'vowel contractions', userLevel: {userLevel},
                    component: <VowelContractions navigateAwayHandler={navigateAwayHandler} />},
                   ],
        'nominals': [{label: 'case endings', userLevel: {userLevel},
                     component: <CaseEndings  navigateAwayHandler={navigateAwayHandler} />},
                     {label: 'kinds of 3rd declension noun',
                      userLevel: {userLevel},
                      component: <KindsOf3rdDeclension  navigateAwayHandler={navigateAwayHandler} />},
                     {label: 'uses of the genitive case',
                      userLevel: {userLevel},
                      component: <GenitiveUses  navigateAwayHandler={navigateAwayHandler} />},
                     {label: 'uses of the dative case',
                      userLevel: {userLevel},
                      component: <DativeUses  navigateAwayHandler={navigateAwayHandler} />},
                    ],
        'verbs': [{label: 'personal endings', userLevel: {userLevel},
                   component: <PersonalEndings  navigateAwayHandler={navigateAwayHandler} />},
                  {label: 'common 2nd aorist verbs', userLevel: {userLevel},
                   component: <Common2ndAorists  navigateAwayHandler={navigateAwayHandler} />},
                  ]
    }
    const [ sectionChosen, setSectionChosen ] = useState('general');
    const [ viewChosen, setViewChosen ] = useState(sections['general'][0].label);

    const changeSection = ( value ) => {
        setSectionChosen(value);
        setViewChosen(sections[value][0].label);
    }

    return(
       <Row key="ReferenceView" className="referenceview-component panel-view">
           <Col>
                <h2>Quick Reference</h2>
                <Form>
                    <Form.Row>
                        <Col>
                            <Form.Control
                                as="select"
                                onChange={e => changeSection(e.target.value)}
                            >
                                {Object.keys(sections).map( key =>
                                    <option key={key}>{key}</option>
                                )}
                            </Form.Control>
                        </Col>
                        <Col>
                            <Form.Control
                                as="select"
                                onChange={e => setViewChosen(e.target.value)}
                            >
                                {sections[sectionChosen].map( s =>
                                    <option key={s.label}>{s.label}</option>
                                )}
                            </Form.Control>
                        </Col>
                    </Form.Row>
                </Form>
                <TransitionGroup className="reference-view-panes">
                    {sections[sectionChosen].map( view =>
                        viewChosen === view.label &&
                        <CSSTransition
                            key={view.label}
                            timeout={0}
                            classNames="reference-view-pane"
                        >
                            <div className="reference-view-pane">
                                {view.component}
                            </div>
                        </CSSTransition>
                    )}
                </TransitionGroup>
           </Col>
       </Row>
    )
}

export default ReferenceView;