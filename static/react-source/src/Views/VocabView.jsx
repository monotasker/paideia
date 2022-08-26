import React, { useEffect, useState, useMemo, useContext, useRef, useLayoutEffect } from "react";
import {
    Alert,
    Badge,
    Button,
    Col,
    Collapse,
    Form,
    OverlayTrigger,
    Row,
    Spinner,
    Table,
    ToggleButton,
    ToggleButtonGroup,
    Tooltip,
} from "react-bootstrap";
import { LinkContainer } from "react-router-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import greekUtils from 'greek-utils/lib/index'

import { fetchVocabulary } from "../Services/stepFetchService";
import { UserContext } from "../UserContext/UserProvider";
import { urlBase } from "../variables";


const LinkHeading = ({ field, label, mySortCol, myOrder, sortHandler,
                       classLabel }) => {
  let myIcon = "";
  let myActiveState = "";
  if (field == mySortCol && myOrder == "asc") {
    myIcon = "sort-down";
    myActiveState = "active";
  } else if (field == mySortCol && myOrder == "desc") {
    myIcon = "sort-up";
    myActiveState = "active";
  } else {
    myIcon = "sort";
    myActiveState = "inactive";
  }
  return (
    <th key={label} className={classLabel}>
      <a href="#" onClick={e => sortHandler(e, field)}
        className="vocabview-sorter-link"
      >
        {label}
        <FontAwesomeIcon icon={myIcon} className={myActiveState} />
      </a>
    </th>
  );
}


const PrincipalParts = ({w}) => {
  let pp = null;
  const principal_parts = [{tense: "future active", form: w['future']},
                             {tense: "aorist active", form: w['aorist_active']},
                             {tense: "perfect active", form: w['perfect_active']},
                             {tense: "aorist passive", form: w['aorist_passive']},
                             {tense: "perfect passive", form: w['perfect_passive']}
                            ];
  if ( principal_parts.some(i => !["", null, "none", undefined].includes(i.form)) ) {
    const myPP = principal_parts.map(p =>
      <li key={`${w.id}_${p.tense}`}>
      <OverlayTrigger placement="top"
        overlay={
          <Tooltip id={`tooltip-${w.id}_${p.tense}`}>
            {!["", null, "none", undefined, "--"].includes(p.form) ?
              `${p.tense} indicative (1p sing.) form of ${w.accented_lemma}` : `${w.accented_lemma} does not appear in the ${p.tense} indicative`}
          </Tooltip>
        }
      >
        <a className={`vocab keyforms verb ${p.tense}`}>
          {!["", null, "none", undefined].includes(p.form) ? <span className={`${p.tense}`}>{p.form}</span> : "--"}
        </a>
      </OverlayTrigger>
      </li>
      );
    pp = (
      <div className="principal-parts">
        <OverlayTrigger placement="top"
          overlay={
            <Tooltip id={`tooltip-pp-label-${w.id}`}>Principal parts: Hover over a form for an explanation</Tooltip>
          }
        >
          <Badge pill className="label">PP</Badge>
        </OverlayTrigger>
        <ul>{myPP}</ul>
      </div>
    );
      }
  else {
    pp = null;
  }
  return pp;
}

const WordRow = ({ w, navigateAwayHandler }) => {
  const [ showDetails, setShowDetails ] = useState(false);
  const parts_of_speech = {
    noun: 'N',
    proper_noun: 'PN',
    verb: 'V',
    adjective: 'Adj',
    adverb: 'Adv',
    preposition: 'Prep',
    conjunction: 'C',
    particle: 'Pt'
  }
  return (
    <tr>
      <td className={`${w.part_of_speech} lemma`}>
        <span className="lemma">{w.accented_lemma}</span>
      {!!w.real_stem && w.real_stem != 'none' ?
        <span className="real-stem">
          <OverlayTrigger placement="top"
            overlay={<Tooltip id={`tooltip-stem-${w.id}`}>Real stem</Tooltip>}
          >
            <span className="label"><FontAwesomeIcon icon="seedling" /></span>
          </OverlayTrigger>
          {w.real_stem}</span>
        : ''}
      {!!w.genitive_singular && w.genitive_singular != 'none' ?
        <span className="gen-sing">
          <OverlayTrigger placement="top"
            overlay={<Tooltip id={`tooltip-gen-sing-${w.id}`}>Genitive singular form</Tooltip>}
          >
            <Badge pill className="label">G</Badge>
          </OverlayTrigger>
          {w.genitive_singular}</span>
        : ''}
      <PrincipalParts w={w} />
      {!["", null, "none", undefined].includes(w['other_irregular']) ?
        <span className="other-irregular">
          <a className="label"
            onClick={() => setShowDetails(!showDetails)}
            aria-controls="other-irregular-content"
            aria-expanded={showDetails}
          >
            <FontAwesomeIcon icon="caret-down" />{!showDetails ? "show more" : "hide"} details
          </a>
          <Collapse in={showDetails}>
            <div className="other-irregular-content">{w.other_irregular}</div>
          </Collapse>
        </span>
        : ''}
    </td>
    <td className={`${w.part_of_speech} part-of-speech`}>
      <Badge pill>{parts_of_speech[w.part_of_speech]}</Badge>
    </td>
    <td className="glosses">
      <ul>{w.glosses.map((g, i) => <li key={i}>{g}</li>)}</ul>
    </td>
    <td className="set-introduced">{w.set_introduced}</td>
    <td className="related-lessons">
        <span className="vocab-videos">{w.videos.map((v, i) => (
          <OverlayTrigger key={i} placement="top"
            overlay={<Tooltip id={`tooltip-video-${w.id}`}>{v[1]}</Tooltip>}
          >
            <Button variant="link" onClick={() => navigateAwayHandler(`/${urlBase}/videos/${v[0]}`)}>
              <FontAwesomeIcon icon="video" />
            </Button>
            {/* <LinkContainer to={`/${urlBase}/videos/${v[0]}`} className="closer-link">
            </LinkContainer> */}
          </OverlayTrigger>
        ))}
      </span>
    </td>
    <td>{w.times_in_nt}</td>
  </tr>
  )
}

// FIXME: Don't fire when pane just flies in!
const vocabIsEqual = (prevProps, nextProps) => {
  // console.log('checking vocab equality');
  const oldWordIDs = JSON.stringify(prevProps.vocab.map(w => w.id));
  const newWordIDs = JSON.stringify(nextProps.vocab.map(w => w.id));
  return oldWordIDs === newWordIDs;
}


const VocabTable = React.memo(({ headings, vocab, sortCol, order, sortHandler, navigateAwayHandler }) => {
  return(
    vocab.length > 0 ? (
      <Table>
        <thead>
          <tr>
            {headings.map(({label, field, classLabel}) => (
              field ?
              <LinkHeading key={label} label={label} classLabel={classLabel} field={field}
                mySortCol={sortCol} myOrder={order} sortHandler={sortHandler}
              /> :
              <th key={label} className={classLabel}>{label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {vocab.map((w, i) => <WordRow w={w}
                                key={`wordrow_${i}`}
                                navigateAwayHandler={navigateAwayHandler}
                                />)
          }
          <tr className="scrollDownTarget">
            {headings.map(({label}) => <td key={label}></td>)}
          </tr>
        </tbody>
      </Table>
      )
      :
      <>
      <Alert variant="warning" className="vocab-no-results-message"><FontAwesomeIcon icon="exclamation-circle" size="lg" /> No results found for this search.</Alert>
      <Alert variant="info" className="vocab-no-results-message second">If you are searching only the vocabulary for certain badge sets, try selecting "all badge sets" in the drop-down menu above.</Alert>
      </>
  )
}, vocabIsEqual);


const VocabView = ({ navigateAwayHandler }) => {

  const compareVocab = (a, b) => {
    const term1 = typeof a[mySortCol] === 'string' ? a[mySortCol].toUpperCase() : (a[mySortCol] || 0);
    const term2 = typeof b[mySortCol] === 'string' ? b[mySortCol].toUpperCase() : (b[mySortCol] || 0);
    const result = term1 > term2 ? 1 : -1;
    return myOrder === "asc" ? result : result * -1;
  }

  const doVocabSort = (words, myCol) => {
    return myCol != "" ? [...words].sort(compareVocab) : words
  }

  const doVocabFilter = (vocabIn, searchLetters, strGk, strEng) => {
    let baseVocab = vocabIn;
    if ( searchLetters.length ) {
      baseVocab = vocabIn.filter(w => {
        return searchLetters.includes(greekUtils.sanitizeDiacritics(w.normalized_lemma[0]).toUpperCase());
      });
    }

    let gkSetFinal = baseVocab;
    if ( strGk != "" ) {
      const strGkSan = greekUtils.sanitizeDiacritics(strGk);
      const gkSetMatched = baseVocab.filter(w => w.normalized_lemma == strGkSan);
      const gkSetFuzzy = baseVocab.filter(
        w => w.normalized_lemma != strGkSan
            && (w.normalized_lemma.includes(strGkSan)
                || w.normalized_other_forms.includes(strGkSan))
      );
      gkSetFinal = gkSetMatched.concat(gkSetFuzzy);
    }
    console.log(gkSetFinal);

    let engSetFinal = gkSetFinal;
    if ( strEng != "" ) {
      const engSetMatched = gkSetFinal.filter(
        w => w.glosses.some(g => g == strEng)
      );
      const engSetFuzzy = gkSetFinal.filter(
        w => w.glosses.some(g => g != strEng && g.includes(strEng))
      );
      engSetFinal = engSetMatched.concat(engSetFuzzy);
    }

    return engSetFinal
  }

  const { user, dispatch } = useContext(UserContext);
  const [ updating, setUpdating ] = useState(false);
  const [ processing, setProcessing] = useState(true);
  const [ mySortCol, setMySortCol ] = useState("normalized_lemma");
  const [ myOrder, setMyOrder ] = useState("asc");
  const [ vocab, setVocab ] = useState([]);
  const sortedVocab = useMemo(
    () => doVocabSort(vocab, mySortCol), [vocab, mySortCol, myOrder]
  );
  const [ searchString, setSearchString ] = useState("");
  const [ searchStringEng, setSearchStringEng ] = useState("");
  const [ searchLetters, setSearchLetters ] = useState([]);
  const filteredVocab = useMemo(
    () => doVocabFilter(sortedVocab, searchLetters, searchString, searchStringEng),
    [sortedVocab, searchLetters, searchString, searchStringEng]
  );
  const [ chosenSets, setChosenSets ] = useState(
    Array.from('x'.repeat(user.currentBadgeSet), (_, i) => 1 + i)
  );
  const restrictedVocab = filteredVocab.filter(
    w => chosenSets.length != 0 ? chosenSets.includes(w['set_introduced']) : true
  );
  const [ displayRange, setDisplayRange ] = useState([0, 20]); // for lazy rendering on scroll
  let lastTableRow = null;  // for lazy rendering on scroll
  let firstTableRow = null;  // for lazy rendering on scroll
  const scrollContainer = useRef(null); // for lazy rendering on scroll

  // set up lazy rendering of vocab list when scrolling
  let scrollDownObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach(entry => {
          if ( entry.intersectionRatio > 0 && !!entry.isIntersecting ) {
            setDisplayRange([displayRange[0], displayRange[1] + 10]);
            observer.disconnect();
          }
        },
        {root: scrollContainer.current,
          threshold: 0
        }
      );
    }
  );

  useLayoutEffect(() => {
    lastTableRow = document.querySelector(".vocabtable-container tbody > tr.scrollDownTarget");
    scrollContainer.current = document.querySelector(".vocabtable-container");

    if (!!lastTableRow && restrictedVocab.length > 19) {
      scrollDownObserver.observe(lastTableRow);
    }

    return (() => {
      if ( !!lastTableRow ) {
        scrollDownObserver.unobserve(lastTableRow)
      }
    });
  },
  [restrictedVocab, displayRange]
  );

  useEffect(() => {
    // console.log('fetching from server');
    setUpdating(true);
    fetchVocabulary({vocab_scope_selector: 0})
    .then(mydata => {
      console.log(mydata);
      setVocab(assembleVocab(mydata.mylemmas));
      window.localStorage.setItem('vocab', JSON.stringify(mydata.mylemmas));
      setUpdating(false);
      setProcessing(false);
    });
  }, []);

  // useEffect(() => {
    // const storedData = window.localStorage.getItem('vocab');
    // if ( storedData ) {
    //   try {
    //     const myvocab = JSON.parse(storedData || "[]");
    //     console.log(myvocab);
    //     setVocab(assembleVocab(myvocab));
    //   } catch(SyntaxError) {
    //     window.localStorage.removeItem('vocab');
    //   }
    // }
  //   setProcessing(false);
  // }, []);

  const sortVocab = (event, mystring) => {
    event.preventDefault();
    if ( mySortCol === mystring ) {
      setMyOrder(myOrder === "asc" ? "desc" : "asc");
    }
    setMySortCol(mystring);
  }

  const assembleVocab = (vocab) => {

    const newVocab = vocab.map((i) => {
      return {...i,
              normalized_lemma: greekUtils.sanitizeDiacritics(i['normalized_lemma']),
              normalized_other_forms: greekUtils.sanitizeDiacritics(i['normalized_other_forms'])
      }
    });
    return newVocab
  }


  const resetAction = () => {
    setSearchString("");
    setSearchStringEng("");
    setChosenSets([]);
    document.getElementById('vocab-search-control').value = "";
    document.getElementById('vocab-search-control-english').value = "";
    document.getElementById('vocab-set-control').value = "all badge sets";
    setDisplayRange([0, 20]);
    setSearchLetters([]);
  }

  const restrictSetsAction = (myString) => {
    if ( myString == "all badge sets" ) {
      setChosenSets([]);
    } else if ( myString.slice(0, 9) == "sets 1 to") {
      setChosenSets(
        Array.from('x'.repeat(user.currentBadgeSet), (_, i) => 1 + i)
      );
    } else {
      setChosenSets([parseInt(myString.slice(4))]);
    }
    setDisplayRange([0, 20]);
  }

  const headings = [
    {label: "Greek word",
     classLabel: "lemma",
     field: "normalized_lemma"},
    {label: "PoS",
     classLabel: "part-of-speech",
     field: "part_of_speech"},
    {label: "Glosses",
     classLabel: "glosses",
     field: null},
    {label: "Set",
     classLabel: "set-introduced",
     field: "set_introduced"},
    {label: "Lessons",
     classLabel: "related-lessons",
     field: null},
    {label: "In NT",
     classLabel: "times-in-nt",
     field: "times_in_nt"}
  ]

  return(
     <Row key="VocabView" className="vocabview-component panel-view">
         <Col>
            <h2>Vocabulary</h2>
            <Form className="vocab-filter-form">
              <Form.Row>
                <Col xs="6" md="4" xl="3">
                  <Form.Group
                    controlId="vocab-search-control"
                    onChange={e => setSearchString(e.target.value)}
                  >
                    <Form.Label><FontAwesomeIcon icon="search" />Greek</Form.Label>
                    <Form.Control placeholder=""></Form.Control>
                  </Form.Group>
                </Col>
                <Col xs="6" md="4" xl="3">
                  <Form.Group
                    controlId="vocab-search-control-english"
                    onChange={e => setSearchStringEng(e.target.value)}
                  >
                    <Form.Label><FontAwesomeIcon icon="search" />English</Form.Label>
                    <Form.Control placeholder=""></Form.Control>
                  </Form.Group>
                </Col>
                <Col xs="10" sm="11" md="3" xl="4">
                  <Form.Group controlId="vocab-set-control">
                    <Form.Label className="vocab-set-filter-label"><FontAwesomeIcon icon="filter" />Badge sets</Form.Label>
                    <Form.Control as="select"
                      onChange={e => restrictSetsAction(e.target.value)}
                    >
                      {!!user.currentBadgeSet &&
                        <option key="0">{`sets 1 to ${user.currentBadgeSet}`}</option>
                      }
                      <option key="1">all badge sets</option>
                      {Array.from('x'.repeat(20), (_, i) => 1 + i).map( n =>
                          <option key={n + 1}>{`set ${n}`}</option>
                      )}
                    </Form.Control>
                  </Form.Group>
                </Col>
                <Col xs="2" sm="1" xl="2">
                  <Button onClick={() => resetAction()}
                  >
                    <FontAwesomeIcon icon="redo-alt" />
                    <span className="d-none d-xl-inline">Clear</span>
                  </Button>
                </Col>
              </Form.Row>
              <Form.Row className="alphabet">
                <div>
                  <ToggleButtonGroup type="checkbox" size="sm"
                    value={searchLetters}
                    onChange={val => setSearchLetters(val)}
                  >
                    {['Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ',  'Φ', 'Χ', 'Ψ', 'Ω'].map( l =>
                      <ToggleButton variant="outline-secondary"
                        value={l} key={l}
                      >{l}</ToggleButton>
                    )}
                  </ToggleButtonGroup>
                </div>
              </Form.Row>
            </Form>
            <div className="vocabtable-container" ref={scrollContainer}>
              {!!processing &&
              <Spinner className="vocabtable-loading-spinner"
                animation="grow"
              />}
              {!!processing ? "" :
                <VocabTable headings={headings}
                  vocab={restrictedVocab.slice(...displayRange)}
                  sortCol={mySortCol} order={myOrder} sortHandler={sortVocab}
                  navigateAwayHandler={navigateAwayHandler}
                />
              }
            </div>
            <div className="vocabview-footer">
              <div className="vocabview updating">{updating ?
                (<span><Spinner animation="grow" size="sm" />{"Checking for updates"}</span>) :
                (<span className="done">Up to date</span>)}
              </div>
              <div className="vocabview displaycount">
                Showing {restrictedVocab.length} out of the total {vocab.length} words.
              </div>
            </div>
         </Col>
     </Row>
  )
}

export default VocabView;