import React, { useState } from 'react';
import {
    ButtonGroup,
    Button
} from "react-bootstrap";
import {
    TransitionGroup,
    CSSTransition
} from "react-transition-group";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import ReferenceView from "../Views/ReferenceView";
import VocabView from "../Views/VocabView";
import QueriesView from "../Views/QueriesView";

const Tools = () => {

    const [openPanel, setOpenPanel] = useState(0);

    const panels = [
        {label: 'Queries',
         icon: "comment",
         component: <QueriesView />},
        {label: 'Reference',
         icon: "bolt",
         component: <ReferenceView />},
        {label: 'Vocab',
         icon: "sort-alpha-down",
         component: <VocabView />},
        // {label: 'Review',
        //  icon: faHistory,
        //  component: ReviewPanel},
        // {label: 'Notes',
        //  icon: faPencilAlt,
        //  component: NotesPanel},
    ]

    return(
        <React.Fragment>
            <ButtonGroup vertical className="tools-component">
                {panels.map( ({ label, icon, component }) =>
                    <Button key={label}
                        value={label}
                        onClick={() => openPanel === label ? setOpenPanel('none') : setOpenPanel(label)}>
                        <FontAwesomeIcon icon={icon} fixedWidth size="lg" />
                        {label}
                    </Button>
                )}
            </ButtonGroup>
            <TransitionGroup className="tool-panels">
                {panels.map( ({ label, icon, component }) =>
                    openPanel === label &&
                    <CSSTransition
                        key={label}
                        timeout={0}
                        classnames="panel-body"
                    >
                        <div className="panel-body">
                            {component}
                        </div>
                    </CSSTransition>
                )}
            </TransitionGroup>
        </React.Fragment>
    )

}

export default Tools;