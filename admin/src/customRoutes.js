import React from 'react';
import { Route } from 'react-router-dom';
import AddGroupToUser from './views/AddGroupToUser';
import EditUser from './views/EditUser';
import AddUserPolicy from './views/AddUserPolicy';
import EditUserPolicy from './views/EditUserPolicy';
import DeleteUserPolicy from './views/DeleteUserPolicy';

export default [
    <Route path="/users/:user/add-to-group" component={AddGroupToUser} />,
    <Route path="/users/:user/policies/add" component={AddUserPolicy} />,
    <Route path="/users/:user/policies/:policy/edit" component={EditUserPolicy} />,
    <Route path="/users/:user/policies/:policy/delete" component={DeleteUserPolicy} />,
    <Route path="/users/:user" component={EditUser} />,
];
