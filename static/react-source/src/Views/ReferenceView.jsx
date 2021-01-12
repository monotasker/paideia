import React, { useState } from "react";
import {
    TransitionGroup,
    CSSTransition
} from "react-transition-group";
import {
    Row,
    Col,
    Table,
    Form
} from "react-bootstrap";
import { useHistory, Link } from "react-router-dom";
import { urlBase } from "../variables";

const CaseEndings = () => (
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
        <p>The full set of case endings is introduced for the first time in <Link to={`/${urlBase}/videos/81`}>lesson 8.1, "The Dative Case"</Link></p>
    </React.Fragment>

)

const SquareOfStops = () => (
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
                    <td>δ</td>
                    <td>θ</td>
                    <td className="spacer"></td>
                    <td>σ</td>
                </tr>
            </tbody>
        </Table>
        <p>Discussed in <Link to={`/${urlBase}/videos/101`}>lesson 10.1, "The Aorist Tense"</Link></p>
    </React.Fragment>
)

const VowelContractions = () => {
    const history = useHistory();

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
                Discussed in <Link to={`/${urlBase}/videos/52`}>lesson 5.2, "The Real Stems of 3rd Declension Nouns"</Link> and in <Link to={`/${urlBase}/videos/73`}>lesson 7.3, "Contract Verbs"</Link>
            </p>
        </React.Fragment>
    )
}

const ReferenceView = () => {

    const sections = {
        'general': [{label: 'square of stops',
                    component: <SquareOfStops />},
                    {label: 'vowel contractions',
                    component: <VowelContractions />},
                   ],
        'nominals': [{label: 'case endings',
                     component: <CaseEndings />},
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