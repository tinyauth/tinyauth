import React from 'react';
import { Route } from 'react-router-dom';
import AddGroupToUser from './views/AddGroupToUser';


export default [
    <Route path="/users/:user/add-to-group" component={AddGroupToUser} />,
];
