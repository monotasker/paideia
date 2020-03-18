import React, { useState, useEffect } from 'react';
import {
    ButtonGroup,
    Button
} from "react-bootstrap";
import {
    TransitionGroup,
    SwitchTransition,
    CSSTransition
} from "react-transition-group";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import ReferenceView from "../Views/ReferenceView";
import VocabView from "../Views/VocabView";
import QueriesView from "../Views/QueriesView";
import SettingsView from "../Views/SettingsView";

const Tools = () => {

    const [openPanel, setOpenPanel] = useState(null);

    useEffect(() => {
      const handleClick = (event) => {
          if ( event.target.closest('.tools-component, .tool-panels, .queries-view-changer, .vocabview-sorter-link') === null ) {
            setOpenPanel(null);
          }
      }
      window.addEventListener("click", handleClick);
      return () => window.removeEventListener("click", handleClick);
    });

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
        {label: 'Settings',
         icon: "sliders-h",
         component: <SettingsView />},
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
                        onClick={() => openPanel === label ? setOpenPanel(null) : setOpenPanel(label)}>
                        <FontAwesomeIcon
                          icon={icon}
                          fixedWidth size="lg"
                        />
                        {label}
                    </Button>
                )}
            </ButtonGroup>
            <div className="tool-panels">
                {panels.map(({ label, icon, component }) =>
                    <CSSTransition
                        key={label}
                        in={label === openPanel}
                        timeout={0}
                        classNames="panel-body"
                        mountOnEnter={true}
                        appear={true}
                    >
                        <div className="panel-body">
                            {component}
                        </div>
                    </CSSTransition>
                )}
            </div>
        </React.Fragment>
    )

}

export default Tools;