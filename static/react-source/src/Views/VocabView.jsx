import React, { useEffect, useState } from "react";
import {
    Row,
    Col,
    Table,
    Form,
    Button,
    OverlayTrigger,
    Tooltip,
    Badge
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import greekUtils from 'greek-utils/lib/index'

import { fetchVocabulary } from "../Services/stepFetchService";

const VocabView = () => {

  const compareVocab = (a, b) => {
    const term1 = typeof a[mySortCol] === 'string' ? a[mySortCol].toUpperCase() : (a[mySortCol] || 0);
    const term2 = typeof b[mySortCol] === 'string' ? b[mySortCol].toUpperCase() : (b[mySortCol] || 0);
    const result = term1 > term2 ? 1 : -1;
    return myOrder === "asc" ? result : result * -1;
  }

  const [ mySortCol, setMySortCol ] = useState("normalized_lemma");
  const [ myOrder, setMyOrder ] = useState("asc");
  const [ vocab, setVocab ] = useState([]);
  const sortedVocab = mySortCol != "" ? [...vocab].sort(compareVocab) : vocab;
  const [ totalCount, setTotalCount ] = useState(0);
  const [ searchString, setSearchString ] = useState("");
  const filteredVocab = sortedVocab.filter(w => searchString != "" ? w['normalized_lemma'].includes(searchString) : true );
  const [ chosenSets, setChosenSets ] = useState([]);
  const restrictedVocab = filteredVocab.filter(w => chosenSets.length != 0 ? chosenSets.includes(w['set_introduced']) : true );

  useEffect(() => {
    fetchVocabulary({vocab_scope_selector: 0})
    .then(mydata => {
      console.log(mydata);
      setVocab(assembleVocab(mydata.mylemmas));
      setTotalCount(mydata.total_count);
    });
  }, []);

  const sortVocab = (event, mystring) => {
    if ( mySortCol === mystring ) {
      setMyOrder(myOrder === "asc" ? "desc" : "asc");
    }
    setMySortCol(mystring);
    event.preventDefault();
  }

  const assembleVocab = (vocab) => {
    const newVocab = vocab.map((i) => {
      return {...i,
              normalized_lemma: greekUtils.sanitizeDiacritics(i['normalized_lemma']),
              key_forms: makeForms(i)
      }
    });
    return newVocab
  }

  const makeForms = (w) => {
    const forms = [];
    if ( !["", null, "none", undefined].includes(w['real_stem']) ) {
      forms.push(<span className='vocab keyforms realstem'>{`real stem: ${w['real_stem']}`}</span>)
    }
    if ( !["", null, "none", undefined].includes(w['genitive_singular']) ) {
      forms.push(<span className='vocab keyforms genitive'>{`gen: ${w['genitive_singular']};`}</span>)
    }
    const principal_parts = [{tense: "future active", form: w['future']},
                             {tense: "aorist active", form: w['aorist_active']},
                             {tense: "perfect active", form: w['perfect_active']},
                             {tense: "aorist passive", form: w['aorist_passive']},
                             {tense: "perfect passive", form: w['perfect_passive']}
                            ];
    if ( principal_parts.some(i => !["", null, "none", undefined].includes(i.form)) ) {
      const myPL = "principal parts: ";
      const myPP = principal_parts.map(p =>
        <OverlayTrigger key={`${w.id}_${p.tense}`} placement="top"
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
        );
      forms.push(<p>{[myPL, ...myPP]}</p>);
    }
    if ( !["", null, "none", undefined].includes(w['other_irregular']) ) {
      forms.push(<p className="vocab keyforms other">
                  {`other irregular forms: ${w['other_irregular']}`}
                 </p>);
    }
    console.log(forms);

    return forms;
  }

  const resetAction = () => {
    setSearchString("");
    setChosenSets([]);
    document.getElementById('vocab-search-control').value = "";
    document.getElementById('vocab-set-control').value = "all sets";
  }

  const WordRow = (props) => {
    return (
      <tr>
        <td className={props.w.part_of_speech}>{props.w.accented_lemma}</td>
        <td className={props.w.part_of_speech}><Badge pill>{parts_of_speech[props.w.part_of_speech]}</Badge></td>
        <td>{props.w.glosses.map((g, i) => <p key={i}>{g}</p>)}</td>
        <td>{props.w.key_forms}</td>
        <td>{props.w.set_introduced}</td>
        <td>{props.w.videos.map((v, i) => <a key={i} href={v[2]}>{v[1]}</a>)}</td>
        <td>{props.w.times_in_nt}</td>
      </tr>
    )
  }

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

  const LinkHeading = (props) => {
    let myIcon = "";
    let myActiveState = "";
    if (props.field == mySortCol && myOrder == "asc") {
      myIcon = "sort-down";
      myActiveState = "active";
    } else if (props.field == mySortCol && myOrder == "desc") {
      myIcon = "sort-up";
      myActiveState = "active";
    } else {
      myIcon = "sort";
      myActiveState = "inactive";
    }
    return (
      <th key={props.label}>
        <a href="#" onClick={e => sortVocab(e, props.field)}
          className="vocabview-sorter-link"
        >
          {props.label}
          <FontAwesomeIcon icon={myIcon} className={myActiveState} />
        </a>
      </th>
    );
  }

  const NonLinkHeading = (props) => {
    return <th key={props.label}>{props.label}</th>;
  }

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
                    <Form.Label><FontAwesomeIcon icon="search" />Search</Form.Label>
                    <Form.Control></Form.Control>
                  </Form.Group>
                </Col>
                <Col>
                  <Form.Group controlId="vocab-set-control">
                    <Form.Label><FontAwesomeIcon icon="filter" />Badge set</Form.Label>
                    <Form.Control as="select"
                      onChange={e => setChosenSets([parseInt(e.target.value.slice(4))])}
                    >
                      <option key="0">all sets</option>
                      {Array.from('x'.repeat(20), (_, i) => 1 + i).map( n =>
                          <option key={n}>{`set ${n}`}</option>
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
            Showing {restrictedVocab.length} out of the total {vocab.length} words used in all interactions.
            <div className="vocabtable-container">
              <Table>
                <thead>
                  <tr>
                    {headings.map(({label, field}) => (
                      field ? <LinkHeading key={label} label={label} field={field} /> : <NonLinkHeading key={label} label={label} />
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {restrictedVocab && restrictedVocab.map(word => <WordRow w={word} key={word.id} />)}
                </tbody>
              </Table>
            </div>
         </Col>
     </Row>
  )
}

export default VocabView;