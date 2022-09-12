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
import ToggleButton from "react-bootstrap/ToggleButton";
import ToggleButtonGroup from "react-bootstrap/ToggleButtonGroup";
// import { useHistory, Link } from "react-router-dom";
import Measure from "react-measure";
import UserProvider, { UserContext } from "../UserContext/UserProvider";
import { urlBase } from "../variables";


const DativeUses = ({navigateAwayHandler}) => (
    <>
        <Table className="dative-uses-table" size="sm">
            <thead>
                <tr>
                    <th colSpan="3">Common Uses of the Dative</th>
                </tr>
                <tr>
                    <th colSpan="3"><small>A = action being modified, D = dative nominal</small></th>
                </tr>
                <tr>
                    <th>Dative of...</th>
                    <th>Relationship to the action</th>
                    <th>Helper words</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Indirect object</td>
                    <td>D is the secondary recipient or target of A</td>
                    <td>"to"</td>
                </tr>
                <tr>
                    <td>Interest</td>
                    <td>A is performed for the sake of D or A benefits D</td>
                    <td>"for"</td>
                </tr>
                <tr>
                    <td>Accompaniment</td>
                    <td>D is with the subject of A during action</td>
                    <td>"with"</td>
                </tr>
                <tr>
                    <td>Time</td>
                    <td>A takes place at the time D</td>
                    <td>"in" or "at" or "during"</td>
                </tr>
                <tr>
                    <td>Place</td>
                    <td>A takes place in the location D</td>
                    <td>"in" or "at"</td>
                </tr>
                <tr>
                    <td>Instrument or means</td>
                    <td>A is performed using D</td>
                    <td>"with" or "using"</td>
                </tr>
                <tr>
                    <td>Context or sphere</td>
                    <td>A takes place in the context of D</td>
                    <td>"in the context of" or "in relation to"</td>
                </tr>
            </tbody>
        </Table>
        <p>The uses of the dative are introduced in <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/81`)}>lesson 8.1, "The Dative Case"</Button></p>
    </>
);

const PersonalEndings = ({navigateAwayHandler}) => {
    const [showPresent, setShowPresent] = useState(true);
    const [showFuture, setShowFuture] = useState(false);
    const [showImperfect, setShowImperfect] = useState(true);
    const [show1stAorist, setShow1stAorist] = useState(false);
    const [show2ndAorist, setShow2ndAorist] = useState(false);
    const [showPerfect, setShowPerfect] = useState(false);
    const [tableWidth, setTableWidth] = useState();
    const wideTable = tableWidth >= 555 ? true : false;
    const buttons = [{label: `pres${!!wideTable ? "ent" : "."}`,
                      value: "present",
                      prop: showPresent,
                      handler: setShowPresent},
                     {label: `fut${!!wideTable ? "ure" : "."}`,
                      value: "future",
                      prop: showFuture,
                      handler: setShowFuture},
                     {label: `imp${!!wideTable ? "erfect" : "."}`,
                      value: "imperfect",
                      prop: showImperfect,
                      handler: setShowImperfect},
                     {label: `1 aor${!!wideTable ? "ist" : "."}`,
                      value: "1 aorist",
                      prop: show1stAorist,
                      handler: setShow1stAorist},
                     {label: `2 aor${!!wideTable ? "ist" : "."}`,
                      value: "2 aorist",
                      prop: show2ndAorist,
                      handler: setShow2ndAorist},
                     {label: `perf${!!wideTable ? "ect" : "."}`,
                      value: "perfect",
                      prop: showPerfect,
                      handler: setShowPerfect}
                    ]

    const caseForms = {'1pActiveSing': {pres: <>λυ<u className="mixed">ω</u></>,
                                   fut: <>λυσ<u className="mixed">ω</u></>,
                                   imp: <>ἐλυ<u>ο</u><b>ν</b></>,
                                   faor:  <>ἐλυσ<u className="mixed">α</u></>,
                                   saor:  <>ἐλαβ<u>ο</u><b>ν</b></>,
                                   perf: <>λελυκ<u className="mixed">α</u></>,
                                   prim: "",
                                   sec: "ν",
                                  },
                      '2pActiveSing': {pres: <>λυ<u className="mixed">ει</u><b>ς</b></>,
                                   fut: <>λυσ<u className="mixed">ει</u><b>ς</b></>,
                                   imp: <>ἐλυ<u>ε</u><b>ς</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>ς</b></>,
                                   saor:  <>ἐλαβ<u>ε</u><b>ς</b></>,
                                   perf: <>λελυκ<u>α</u><b>ς</b></>,
                                   prim: "ς",
                                   sec: "ς",
                                  },
                      '3pActiveSing': {pres: <>λυ<u>ε</u><b>ι</b></>,
                                   fut: <>λυσ<u>ε</u><b>ι</b></>,
                                   imp: <>ἐλυ<u>ε</u><b>(ν)</b></>,
                                   faor:  <>ἐλυσ<u className="mixed">ε</u><b>(ν)</b></>,
                                   saor:  <>ἐλαβ<u>ε</u><b>(ν)</b></>,
                                   perf: <>λελυκ<u>ε</u><b>ν</b></>,
                                   prim: "ι",
                                   sec: "(ν)",
                                  },
                      '1pActivePlur': {pres: <>λυ<u>ο</u><b>μεν</b></>,
                                   fut: <>λυσ<u>ο</u><b>μεν</b></>,
                                   imp: <>ἐλυ<u>ο</u><b>μεν</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>μεν</b></>,
                                   saor:  <>ἐλαβ<u>ο</u><b>μεν</b></>,
                                   perf: <>λελυκ<u>α</u><b>μεν</b></>,
                                   prim: "μεν",
                                   sec: "μεν",
                                  },
                      '2pActivePlur': {pres: <>λυ<u>ε</u><b>τε</b></>,
                                   fut: <>λυσ<u>ε</u><b>τε</b></>,
                                   imp: <>ἐλυ<u>ε</u><b>τε</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>τε</b></>,
                                   saor:  <>ἐλαβ<u>ε</u><b>τε</b></>,
                                   perf: <>λελυκ<u>α</u><b>τε</b></>,
                                   prim: "τε",
                                   sec: "τε",
                                  },
                      '3pActivePlur': {pres: <>λυ<u className="mixed">ου</u><b>σι(ν)</b></>,
                                   fut: <>λυσ<u className="mixed">ου</u><b>σι(ν)</b></>,
                                   imp: <>ἐλυ<u>ο</u><b>ν</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>ν</b></>,
                                   saor:  <>ἐλαβ<u>ο</u><b>ν</b></>,
                                   perf: <>λελυκ<u>α</u><b>ν</b></>,
                                   prim: "νσι(ν)",
                                   sec: "ν",
                                  },
                      '1pMiddleSing': {pres: <>λυ<u>ο</u><b>μαι</b></>,
                                   fut: <>λυσ<u>ο</u><b>μαι</b></>,
                                   imp: <>ἐλυ<u>ο</u><b>μην</b></>,
                                   faor:  <>ἐλυσ<u>α</u>μην</>,
                                   saor:  <>ἐγεν<u>ο</u><b>μην</b></>,
                                   perf: <>λελυ<b>μαι</b></>,
                                   prim: "μαι",
                                   sec: "μην",
                                  },
                      '2pMiddleSing': {pres: <>λυ<u className="mixed">ῃ</u></>,
                                   fut: <>λυσ<u className="mixed">ῃ</u></>,
                                   imp: <>ἐλυ<u className="mixed">ου</u></>,
                                   faor:  <>ἐλυσ<u className="mixed">ω</u></>,
                                   saor:  <>ἐγεν<u className="mixed">ου</u></>,
                                   perf: <>λελυ<b>σαι</b></>,
                                   prim: "σαι",
                                   sec: "σο",
                                  },
                      '3pMiddleSing': {pres: <>λυ<u>ε</u><b>ται</b></>,
                                   fut: <>λυσ<u>ε</u><b>ται</b></>,
                                   imp: <>ἐλυσ<u>ε</u><b>το</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>το</b></>,
                                   saor:  <>ἐγεν<u>ε</u><b>το</b></>,
                                   perf: <>λελυ<b>ται</b></>,
                                   prim: "ται",
                                   sec: "το",
                                  },
                      '1pMiddlePlur': {pres: <>λυ<u>ο</u><b>μεθα</b></>,
                                   fut: <>λυσ<u>ο</u><b>μεθα</b></>,
                                   imp: <>ἐλυ<u>ο</u><b>μεθα</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>μεθα</b></>,
                                   saor:  <>ἐγεν<u>ο</u><b>μεθα</b></>,
                                   perf: <>λελυ<b>μεθα</b></>,
                                   prim: "μεθα",
                                   sec: "μεθα",
                                  },
                      '2pMiddlePlur': {pres: <>λυ<u>ε</u><b>σθε</b></>,
                                   fut: <>λυσ<u>ε</u><b>σθε</b></>,
                                   imp: <>ἐλυ<u>ε</u><b>σθε</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>σθε</b></>,
                                   saor:  <>ἐγεν<u>ε</u><b>σθε</b></>,
                                   perf: <>λελυ<b>σθε</b></>,
                                   prim: "σθε",
                                   sec: "σθε",
                                  },
                      '3pMiddlePlur': {pres: <>λυ<u>ο</u><b>νται</b></>,
                                   fut: <>λυσ<u>ο</u><b>νται</b></>,
                                   imp: <>ἐλυ<u>ο</u><b>ντο</b></>,
                                   faor:  <>ἐλυσ<u>α</u><b>ντο</b></>,
                                   saor:  <>ἐγεν<u>ο</u><b>ντο</b></>,
                                   perf: <>λελυ<b>νται</b></>,
                                   prim: "νται",
                                   sec: "ντο",
                                  },
    }
    const TableRow = ({pres, fut, imp, faor, saor, perf, prim, sec}) => (
        <>
        <td>-{prim}
            <ul>
                {!!showPresent &&
                <li>
                    <small className="person-example-present"><span className="tense-label">present:</span> {pres}</small>
                </li>
                }
                {!!showFuture &&
                <li>
                    <small className="person-example-future"><span className="tense-label">future:</span> {fut}</small>
                </li>
                }
                {!!showPerfect &&
                <li>
                    <small className="person-example-perfect"><span className="tense-label">perfect:</span> {perf}</small>
                </li>
                }
            </ul>

        </td>
        <td className="spacer"></td>
        <td>-{sec}<br />
            <ul>
                {!!showImperfect &&
                <li>
                    <small className="person-example-imperfect"><span className="tense-label">imperfect:</span> {imp}</small>
                </li>
                }
                {!!show1stAorist &&
                <li>
                    <small className="person-example-1st-aorist"><span className="tense-label">1st aorist:</span> {faor}</small>
                </li>
                }
                {!!show2ndAorist &&
                <li>
                    <small className="person-example-2nd-aorist"><span className="tense-label">2nd aorist:</span> {saor}</small>
                </li>
                }
            </ul>
        </td>
        </>
    )

    return(
    <>
    <Measure bounds onResize={t => setTableWidth(t.bounds.width)}>
        {({measureRef}) => (
        <Table className="personal-endings-table" size="sm" ref={measureRef}>
            <thead>
                <tr>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th colSpan="3">Personal Endings</th>
                </tr>
                <tr>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th>Primary tenses</th>
                    <th className="spacer"></th>
                    <th>Secondary tenses</th>
                </tr>
                <tr>
                    <th></th>
                    <th></th>
                    <th></th>
                    <th>
                        <small>with examples from</small><br />
                        <ToggleButtonGroup className="mb-2"
                            type="checkbox"
                            name="tenses"
                            // vertical={tableWidth >= 500 ? false : true}
                            size="sm"
                            defaultValue={buttons.map(b => ["present", "future", "perfect"].includes(b.value) && b.prop===true && b.value)}
                        >
                        {buttons.map(b => ["present", "future", "perfect"].includes(b.value) &&
                            <ToggleButton
                                id={`toggle-${b.value}`}
                                key={`toggle-${b.value}`}
                                type="checkbox"
                                name="tenses"
                                variant="outline-secondary"
                                checked={b.prop}
                                value={b.value}
                                onChange={(e) => b.handler(!b.prop)}
                            >
                                {b.label}
                            </ToggleButton>
                        )}
                        </ToggleButtonGroup>
                    </th>
                    <th className="spacer"></th>
                    <th>
                        <small>with examples from</small><br/>
                        <ToggleButtonGroup className="mb-2"
                            type="checkbox"
                            name="tenses"
                            // vertical={tableWidth >= 500 ? false : true}
                            size="sm"
                            defaultValue={buttons.map(b => ["imperfect", "1 aorist", "2 aorist"].includes(b.value) && b.prop===true && b.value)}
                        >
                        {buttons.map(b => ["imperfect", "1 aorist", "2 aorist"].includes(b.value) &&
                            <ToggleButton
                                id={`toggle-${b.value}`}
                                key={`toggle-${b.value}`}
                                type="checkbox"
                                name="tenses"
                                variant="outline-secondary"
                                checked={b.prop}
                                value={b.value}
                                onChange={(e) => b.handler(!b.prop)}
                            >
                                {b.label}
                            </ToggleButton>
                        )}
                        </ToggleButtonGroup>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th rowSpan="7">Active</th>
                    <th rowSpan="3">sing.</th>
                    <th><span className="person-numeral">1</span>st p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["1pActiveSing"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">2</span>nd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["2pActiveSing"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">3</span>rd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["3pActiveSing"]} />
                </tr>
                <tr>
                    <td className="spacer" colSpan="6"></td>
                </tr>
                <tr>
                    <th rowSpan="3">plur.</th>
                    <th><span className="person-numeral">1</span>st p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["1pActivePlur"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">2</span>nd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["2pActivePlur"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">3</span>rd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["3pActivePlur"]} />
                </tr>
                <tr>
                    <td className="spacer" colSpan="6"></td>
                </tr>
                <tr>
                    <th rowSpan="7">Middle/Passive</th>
                    <th rowSpan="3">sing.</th>
                    <th><span className="person-numeral">1</span>st p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["1pMiddleSing"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">2</span>nd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["2pMiddleSing"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">3</span>rd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["3pMiddleSing"]} />
                </tr>
                <tr>
                    <td className="spacer" colSpan="6"></td>
                </tr>
                <tr>
                    <th rowSpan="3">plur.</th>
                    <th><span className="person-numeral">1</span>st p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["1pMiddlePlur"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">2</span>nd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["2pMiddlePlur"]} />
                </tr>
                <tr>
                    <th><span className="person-numeral">3</span>rd p{tableWidth >= 555 ? "erson" : "."}</th>
                    <TableRow {...caseForms["3pMiddlePlur"]} />
                </tr>
            </tbody>
        </Table>
        )}
    </Measure>
    </>
);
}

const KindsOf3rdDeclension = ({navigateAwayHandler}) => (
    <>
    </>
);

const Common2ndAorists = ({navigateAwayHandler}) => (
    <>
        <Table className="common-aorists-table">
            <thead>
                <tr>
                    <th colSpan="3">Common 2nd Aorist Verbs</th>
                </tr>
                <tr>
                    <th>Present act. ind.</th>
                    <th>Real Stem</th>
                    <th>2nd Aorist act. ind.</th>
                </tr>
            </thead>
            <tbody>
                <tr className="set-9">
                    <td>ἄγω</td>
                    <td>ἀγ(αγ)-</td>
                    <td>ἤγαγον</td>
                </tr>
                <tr classNAme="set-10">
                    <td>ἀποθνῄσκω</td>
                    <td>ἀποθαν-</td>
                    <td>ἀπεθανον</td>
                </tr>
                <tr className="set-">
                    <td>βάλλω</td>
                    <td>βαλ-</td>
                    <td>ἔβαλον</td>
                </tr>
                <tr className="set-">
                    <td>γίνομαι</td>
                    <td>γεν-</td>
                    <td>ἔγνων</td>
                </tr>
                <tr className="set-">
                    <td>ἔρχομαι</td>
                    <td>ελθ-</td>
                    <td>ἤλθον</td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
                <tr className="set-">
                    <td></td>
                    <td></td>
                </tr>
            </tbody>
        </Table>
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

const CaseEndings = ({navigateAwayHandler, userLevel, filterByLevel}) => {
    console.log(`filterByLevel: ${filterByLevel}`);
    return(
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
            {(!filterByLevel || (!!userLevel && userLevel >= 5)) &&
             <>
                <tr>
                    <th>gen sing</th>
                    <td>υ</td>
                    <td>ς</td>
                    <td>υ</td>
                    <td className="spacer"></td>
                    <td>ος</td>
                    <td>ος</td>
                </tr>
                {(!filterByLevel || (!!userLevel && userLevel >= 8)) &&
                    <tr>
                        <th>dat sing</th>
                        <td>ι</td>
                        <td>ι</td>
                        <td>ι</td>
                        <td className="spacer"></td>
                        <td>ι</td>
                        <td>ι</td>
                    </tr>
                }
                {(!filterByLevel || (!!userLevel && userLevel >= 7)) &&
                    <tr>
                        <th>acc sing</th>
                        <td>ν</td>
                        <td>ν</td>
                        <td>ν</td>
                        <td className="spacer"></td>
                        <td>α/ν</td>
                        <td>-</td>
                    </tr>
                }
                {(!filterByLevel || (!!userLevel && userLevel >= 3)) &&
                <tr>
                    <th>voc sing</th>
                    <td>ε</td>
                    <td>-</td>
                    <td>ν</td>
                    <td className="spacer"></td>
                    <td>-</td>
                    <td>-</td>
                </tr>
                }
                <tr>
                    <td colSpan="7" className="spacer"></td>
                </tr>
                {(!filterByLevel || (!!userLevel && userLevel >= 6)) &&
                <>
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
                {(!filterByLevel || (!!userLevel && userLevel >= 8)) &&
                <tr>
                    <th>dat plur</th>
                    <td>ις</td>
                    <td>ις</td>
                    <td>ις</td>
                    <td className="spacer"></td>
                    <td>σι(ν)</td>
                    <td>σι(ν)</td>
                </tr>
                }
                {(!filterByLevel || (!!userLevel && userLevel >= 7)) &&
                <tr>
                    <th>acc plur</th>
                    <td>υς</td>
                    <td>ς</td>
                    <td>α</td>
                    <td className="spacer"></td>
                    <td>ας</td>
                    <td>α</td>
                </tr>
                }
                <tr>
                    <th>voc plur</th>
                    <td>ι</td>
                    <td>ι</td>
                    <td>α</td>
                    <td className="spacer"></td>
                    <td>ες</td>
                    <td>α</td>
                </tr>
                </>
                }
              </>
            }
            </tbody>
        </Table>
        <p>The full set of case endings is introduced for the first time in <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/81`)}>lesson 8.1, "The Dative Case"</Button></p>
    </React.Fragment>
)}

const SquareOfStops = ({navigateAwayHandler, user, filterByLevel}) => (
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

const VowelContractions = ({navigateAwayHandler, userLevel, filterByLevel}) => {
    return (
        <React.Fragment>
            <Table className="vowel-contractions-tableA" size="sm">
                <thead>
                    <tr>
                        <th className="spacer"></th>
                        <th className="spacer"></th>
                        <th colSpan="3">Short Vowel Combinations</th>
                    </tr>
                    <tr>
                        <th className="spacer"></th>
                        <th className="spacer"></th>
                        <th colSpan="3">connecting vowel for ending</th>
                    </tr>
                    <tr>
                        <th className="spacer"></th>
                        <th className="spacer"></th>
                        <th>α</th>
                        <th>ε</th>
                        <th>ο</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th rowSpan="4">final vowel of stem</th>
                    </tr>
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
                        <th className="spacer"></th>
                        <th className="spacer"></th>
                        <th colSpan="3">With Long Vowels/Diphthongs</th>
                    </tr>
                    <tr>
                        <th className="spacer"></th>
                        <th className="spacer"></th>
                        <th colSpan="3">connecting vowel for ending</th>
                    </tr>
                    <tr>
                        <th className="spacer"></th>
                        <th className="spacer"></th>
                        <th>ω</th>
                        <th>ου</th>
                        <th>ει</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th rowSpan="4">final vowel of stem</th>
                    </tr>
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

    const { user, } = useContext(UserContext);
    const userLevel = user.currentBadgeSet;
    const [ filterByLevel, setFilterByLevel ] = useState(userLevel!==null ? true : false);
    console.log(`userLevel: ${typeof(userLevel)}`);
    const commonProps = {navigateAwayHandler: navigateAwayHandler,
                         userLevel: userLevel,
                         filterByLevel: filterByLevel
                        };

    const sections = [
        {label: 'general',
         level: 5,
         views: [{label: 'square of stops',
                  level: 10,
                  component: <SquareOfStops {...commonProps} />},
                 {label: 'vowel contractions',
                  level: 5,
                  component: <VowelContractions  {...commonProps} />},
                 ]
         },
        {label: 'nominals',
         level: 1,
         views: [{label: 'case endings',
                  level: 1,
                  component: <CaseEndings  {...commonProps} />},
                 {label: 'kinds of 3rd declension noun',
                  level: 5,
                  component: <KindsOf3rdDeclension  {...commonProps} />},
                 {label: 'uses of the genitive case',
                  level: 5,
                  component: <GenitiveUses {...commonProps} />},
                 {label: 'uses of the dative case',
                  level: 8,
                  component: <DativeUses {...commonProps} />},
                 ]
         },
        {label: 'verbs',
         level: 7,
         views: [{label: 'personal endings',
                  level: 7,
                  component: <PersonalEndings {...commonProps} />},
                 {label: 'common 2nd aorist verbs',
                  level: 10,
                  component: <Common2ndAorists {...commonProps} />},
                ]
         }
    ];
    const [ sectionChosen, setSectionChosen ] = useState(sections
        .filter(s => (!filterByLevel || (userLevel!==null && s.level <= userLevel) || (userLevel===null)))[0].label);
    const [ viewChosen, setViewChosen ] = useState(
        sections.filter(s => s.label===sectionChosen)[0].views[0].label);

    const changeSection = ( value ) => {
        setSectionChosen(value);
        setViewChosen(sections.filter(s => s.label===value)[0].views[0].label);
    }

    console.log(`filterByLevel: ${filterByLevel}`);
    console.log(`userLevel: ${userLevel}`);

    return(
       <Row key="ReferenceView" className="referenceview-component panel-view">
           <Col>
                <h2>Quick Reference</h2>
                <Form>
                    <Row>
                        <Col>
                            <Form.Control
                                as="select"
                                onChange={e => changeSection(e.target.value)}
                            >
                                {sections
                                   .filter(s => (!filterByLevel || (userLevel!==null && s.level <= userLevel) ||
                                   (userLevel===null)))
                                   .map( s => <option key={s.label}>{s.label}</option>)
                                }
                            </Form.Control>
                        </Col>
                        <Col>
                            <Form.Control
                                as="select"
                                onChange={e => setViewChosen(e.target.value)}
                            >
                                {sections
                                    .filter(s => s.label===sectionChosen)[0].views
                                    .filter(s => (!filterByLevel || (userLevel!==null && s.level <= userLevel)
                                    || (userLevel===null)))
                                    .map( s =>
                                    <option key={s.label}>{s.label}</option>
                                )}
                            </Form.Control>
                        </Col>
                    </Row>
                    {userLevel!==null &&
                    <Row>
                        <Col className="filter-content-switch-col">
                            <Form.Check inline label="Only show content I've learned so far"
                            id="only-unread-checkbox"
                            type="switch"
                            // defaultValue={filterUnread}
                            checked={filterByLevel}
                            onChange={e => setFilterByLevel(!filterByLevel)}
                            />
                        </Col>
                    </Row>
                    }
                </Form>
                <TransitionGroup className="reference-view-panes">
                    {sections.filter(s => s.label===sectionChosen)[0].views.map( view =>
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