import React, { useEffect, useState, useMemo, useContext } from "react";
import {
    Row,
    Col,
    Table,
    Form,
    Button,
    OverlayTrigger,
    Tooltip,
    Badge,
    Spinner
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import greekUtils from 'greek-utils/lib/index'

import { fetchVocabulary } from "../Services/stepFetchService";
import { UserContext } from "../UserContext/UserProvider";


const LinkHeading = ({ field, label, mySortCol, myOrder, sortHandler }) => {
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
    <th key={label}>
      <a href="#" onClick={e => sortHandler(e, field)}
        className="vocabview-sorter-link"
      >
        {label}
        <FontAwesomeIcon icon={myIcon} className={myActiveState} />
      </a>
    </th>
  );
}


const WordRow = ({ w }) => {
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
  console.log('word row rendering');
  return (
    <tr>
      <td className={w.part_of_speech}>{w.accented_lemma}</td>
      <td className={w.part_of_speech}><Badge pill>{parts_of_speech[w.part_of_speech]}</Badge></td>
      <td><ul>{w.glosses.map((g, i) => <li key={i}>{g}</li>)}</ul></td>
      <td>{w.key_forms}</td>
      <td>{w.set_introduced}</td>
      <td><ul>{w.videos.map((v, i) => <li key={i}><a href={v[2]}>{v[1]}</a></li>)}</ul></td>
      <td>{w.times_in_nt}</td>
    </tr>
  )
}


const vocabIsEqual = (prevProps, nextProps) => {
  console.log('checking vocab equality');
  const oldWordIDs = JSON.stringify(prevProps.vocab.map(w => w.id));
  const newWordIDs = JSON.stringify(nextProps.vocab.map(w => w.id));
  return oldWordIDs === newWordIDs;
}


const VocabTable = React.memo(({ headings, vocab, sortCol, order, sortHandler }) => {
  return(
    <Table>
      <thead>
        <tr>
          {headings.map(({label, field}) => (
            field ?
            <LinkHeading key={label} label={label} field={field}
              mySortCol={sortCol} myOrder={order} sortHandler={sortHandler}
            /> :
            <th key={label}>{label}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {vocab.map(w => <WordRow w={w} key={`wordrow_${w.id}`} />)}
      </tbody>
    </Table>
  )
}, vocabIsEqual);

const VocabView = (props) => {

  const compareVocab = (a, b) => {
    const term1 = typeof a[mySortCol] === 'string' ? a[mySortCol].toUpperCase() : (a[mySortCol] || 0);
    const term2 = typeof b[mySortCol] === 'string' ? b[mySortCol].toUpperCase() : (b[mySortCol] || 0);
    const result = term1 > term2 ? 1 : -1;
    return myOrder === "asc" ? result : result * -1;
  }

  const doVocabSort = (words, myCol) => {
    return myCol != "" ? [...words].sort(compareVocab) : words
  }

  const doVocabFilter = (vocabIn, strGk, strEng) => {
    console.log(vocabIn.length);

    let gkSetFinal = vocabIn;
    if ( strGk != "" ) {
      const strGkSan = greekUtils.sanitizeDiacritics(strGk);
      const gkSetMatched = vocabIn.filter(w => w.normalized_lemma == strGkSan);
      console.log(gkSetMatched.length);
      const gkSetFuzzy = vocabIn.filter(
        w => w.normalized_lemma != strGkSan && w.normalized_lemma.includes(strGkSan)
      );
      gkSetFinal = gkSetMatched.concat(gkSetFuzzy);
      console.log(gkSetFinal.length);
    }

    let engSetFinal = gkSetFinal;
    if ( strEng != "" ) {
      const engSetMatched = gkSetFinal.filter(
        w => w.glosses.some(g => g == strEng)
      );
      console.log(engSetMatched.length);
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
  const filteredVocab = useMemo(
    () => doVocabFilter(sortedVocab, searchString, searchStringEng),
    [sortedVocab, searchString, searchStringEng]
  );
  const [ chosenSets, setChosenSets ] = useState(
    Array.from('x'.repeat(user.currentBadgeSet), (_, i) => 1 + i)
  );
  const restrictedVocab = filteredVocab.filter(
    w => chosenSets.length != 0 ? chosenSets.includes(w['set_introduced']) : true
  );

  useEffect(() => {
    console.log('fetching from server');
    setUpdating(true);
    fetchVocabulary({vocab_scope_selector: 0})
    .then(mydata => {
      console.log(mydata);
      setVocab(assembleVocab(mydata.mylemmas));
      window.localStorage.setItem('vocab', JSON.stringify(mydata.mylemmas));
      setUpdating(false);
    });
  }, []);

  useEffect(() => {
    window.setTimeout(1);
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
    setProcessing(false);
  }, []);

  const sortVocab = (event, mystring) => {
    console.log('fired with', mystring);
    event.preventDefault();
    if ( mySortCol === mystring ) {
      setMyOrder(myOrder === "asc" ? "desc" : "asc");
    }
    setMySortCol(mystring);
  }

  const assembleVocab = (vocab) => {
    console.log('assembling vocab');

    const newVocab = vocab.map((i) => {
      return {...i,
              normalized_lemma: greekUtils.sanitizeDiacritics(i['normalized_lemma']),
              key_forms: makeForms(i)
      }
    });
    return newVocab
  }

  const makeForms = (w) => {
    console.log('making forms');
    const forms = [];
    if ( !["", null, "none", undefined].includes(w['real_stem']) ) {
      forms.push(<span key="realstem" className='vocab keyforms realstem'>
                  {`real stem: ${w['real_stem']}`}
                 </span>);
    }
    if ( !["", null, "none", undefined].includes(w['genitive_singular']) ) {
      forms.push(<span key="gen" className='vocab keyforms genitive'>
                  {`gen: ${w['genitive_singular']};`}
                 </span>);
    }
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
              {!["", null, "none", undefined].includes(p.form) ?
                `${p.tense} indicative (1p sing.) form of ${w.accented_lemma}` : `${w.accented_lemma} does not appear in the ${p.tense} indicative`}
            </Tooltip>
          }
        >
          <a className={`vocab keyforms verb ${p.tense}`}>
           {!["", null, "none", undefined].includes(p.form) ? <span className={`${p.tense}`}>{p.form} </span> : "--"}
          </a>
        </OverlayTrigger>
        </li>
        );
      forms.push(<div key="pps" className="vocab keyforms pps">
                  principal parts:<ul>{myPP}</ul>
                 </div>);
    }
    if ( !["", null, "none", undefined].includes(w['other_irregular']) ) {
      forms.push(<div key="other" className="vocab keyforms other">
                  {`other irregular forms: ${w['other_irregular']}`}
                 </div>);
    }
    // console.log(forms);

    return forms;
  }

  const resetAction = () => {
    setSearchString("");
    setSearchStringEng("");
    setChosenSets([]);
    document.getElementById('vocab-search-control').value = "";
    document.getElementById('vocab-search-control-english').value = "";
    document.getElementById('vocab-set-control').value = "all badge sets";
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
  }

  const headings = [
    {label: "Dictionary form",
     field: "normalized_lemma"},
    {label: "PoS",
     field: "part_of_speech"},
    {label: "Glosses",
     field: null},
    {label: "Key forms",
     field: null},
    {label: "Set",
     field: "set_introduced"},
    {label: "Video",
     field: null},
    {label: "In NT",
     field: "times_in_nt"}
  ]

  return(
     <Row key="VocabView" className="vocabview-component panel-view">
         <Col>
            <h2>Vocabulary</h2>
            <Form>
              <Form.Row>
                <Col>
                  <Form.Group
                    controlId="vocab-search-control"
                    onChange={e => setSearchString(e.target.value)}
                  >
                    {/* <Form.Label><FontAwesomeIcon icon="search" />Search</Form.Label> */}
                    <Form.Control placeholder="Search Greek words"
                    ></Form.Control>
                  </Form.Group>
                </Col>
                <Col>
                  <Form.Group
                    controlId="vocab-search-control-english"
                    onChange={e => setSearchStringEng(e.target.value)}
                  >
                    {/* <Form.Label><FontAwesomeIcon icon="search" />Search</Form.Label> */}
                    <Form.Control placeholder="Search English glosses"
                    ></Form.Control>
                  </Form.Group>
                </Col>
                <Col>
                  <Form.Group controlId="vocab-set-control">
                    {/* <Form.Label><FontAwesomeIcon icon="filter" />Badge set</Form.Label> */}
                    <Form.Control as="select"
                      onChange={e => restrictSetsAction(e.target.value)}
                    >
                      <option key="0">{`sets 1 to ${user.currentBadgeSet}`}</option>
                      <option key="1">all badge sets</option>
                      {Array.from('x'.repeat(20), (_, i) => 1 + i).map( n =>
                          <option key={n + 1}>{`set ${n}`}</option>
                      )}
                    </Form.Control>
                  </Form.Group>
                </Col>
                <Col>
                  <Button onClick={() => resetAction()}
                  >
                    <FontAwesomeIcon icon="redo-alt" />
                    Clear
                  </Button>
                </Col>
              </Form.Row>
            </Form>
            <div className="vocabtable-container">{processing ? "" :
                <VocabTable headings={headings} vocab={restrictedVocab}
                  sortCol={mySortCol} order={myOrder} sortHandler={sortVocab}
                />
            }
                <Spinner animation="grow" />
            </div>
            <span className="vocabview updating">{updating ?
              (<span><Spinner animation="grow" />{"Checking for updates"}</span>) :
              (<span className="done">Up to date</span>)}
            </span>
            <span className="vocabview displaycount">
              Showing {restrictedVocab.length} out of the total {vocab.length} words.
            </span>
         </Col>
     </Row>
  )
}

export default VocabView;