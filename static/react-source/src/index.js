import 'bootstrap/dist/css/bootstrap.min.css';

import React from 'react';
import ReactDOM from 'react-dom';
// const crypto = require('crypto');

import './index.css';
import Main from './Views/Main';
import * as serviceWorker from './serviceWorker';

const __webpack_nonce__ =  "blabla"; // crypto.randomBytes(16).toString('base64');

ReactDOM.render(<Main />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.register();
