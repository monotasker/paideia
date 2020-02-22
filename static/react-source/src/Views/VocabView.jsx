import React, { useEffect, useState } from "react";
import {
    Row,
    Col,
    Table,
    Form
} from "react-bootstrap";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { fetchVocabulary } from "../Services/stepFetchService";

const VocabView = () => {

  const compareVocab = (a, b) => {
    const term1 = typeof a[mySortCol] === 'string' ? a[mySortCol].toUpperCase() : a * -1;
    const term2 = typeof b[mySortCol] === 'string' ? b[mySortCol].toUpperCase() : b * -1;
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
  console.log(chosenSets);
  console.log(chosenSets.length != 0);
  console.log(restrictedVocab);


  useEffect(() => {
    fetchVocabulary({vocab_scope_selector: 0})
    .then(mydata => {
      console.log(mydata);
      setVocab(mydata.mylemmas);
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

  const makeForms = (word) => {
    return "";
  }

  const WordRow = (props) => {
    return (
      <tr>
        <td>{props.w.accented_lemma}</td>
        <td>{props.w.part_of_speech}</td>
        <td>{props.w.glosses.join(', ')}</td>
        <td>{makeForms(props.w)}</td>
        <td>{props.w.set_introduced}</td>
        <td>{props.w.videos}</td>
        <td>{props.w.times_in_nt}</td>
      </tr>
    )
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
                      {Array.from('x'.repeat(20), (_, i) => 1 + i).map( n =>
                          <option key={n}>{`set ${n}`}</option>
                      )}
                    </Form.Control>
                  </Form.Group>
                </Col>
              </Form.Row>
            </Form>
            <div className="vocabtable-container">
              <Table>
                <thead>
                  <tr>
                    <th><a href="#" onClick={e => sortVocab(e, "normalized_lemma")}>Dictionary form</a></th>
                    <th><a href="#" onClick={e => sortVocab(e, "part_of_speech")}>Part of speech</a></th>
                    <th>Glosses</th>
                    <th>Key forms</th>
                    <th><a href="#" onClick={e => sortVocab(e, "set_introduced")}>Badge set</a></th>
                    <th>Video</th>
                    <th><a href="#" onClick={e => sortVocab(e, "times_in_nt")}>Time in NT</a></th>
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