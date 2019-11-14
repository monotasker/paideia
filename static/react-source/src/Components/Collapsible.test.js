import React from 'react';
import Collapsible from "./Collapsible";
import renderer from "react-test-renderer";

test('Pane opens and collapses when title is clicked', () => {
  const component = renderer.create(
    <Collapsible titleText="My title" titleElement="h4" />
  );
  const title = component.root.findByType('a');

  //starting state
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
  expect(title.props["aria-expanded"]).toBe(false);

  // manually trigger event
  title.props.onClick();
  // re-render
  tree = component.toJSON();
  expect(tree).toMatchSnapshot();
  expect(title.props["aria-expanded"]).toBe(true);

  // manually trigger event
  title.props.onClick();
  // re-render
  tree = component.toJSON();
  expect(tree).toMatchSnapshot();
  expect(title.props["aria-expanded"]).toBe(false);
});



    // <div class="card">
    //   <div class="card-body">
    //     <a aria-controls="collapse-pane" aria-expanded="false">
    //       <h4>How Do I Switch to a Greek Keyboard?
    //         <svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="plus" class="svg-inline--fa fa-plus fa-w-14 fa-pull-right " role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="currentColor" d="M416 208H272V64c0-17.67-14.33-32-32-32h-32c-17.67 0-32 14.33-32 32v144H32c-17.67 0-32 14.33-32 32v32c0 17.67 14.33 32 32 32h144v144c0 17.67 14.33 32 32 32h32c17.67 0 32-14.33 32-32V304h144c17.67 0 32-14.33 32-32v-32c0-17.67-14.33-32-32-32z"></path></svg>
    //       </h4>
    //     </a>
    //     <div id="switching-pane" class="collapse">
    //     </div>
    //   </div>
    // </div>
