import React from 'react';

import { Admin, Resource } from 'admin-on-rest';

import UserIcon from 'material-ui/svg-icons/social/person';
import GroupIcon from 'material-ui/svg-icons/social/group';

import { Delete } from 'admin-on-rest/lib/mui';

import { UserList, UserCreate, UserEdit } from './views/User';
import { GroupList, GroupCreate, GroupEdit } from './views/Group';

import restClient from './restClient';
import authClient from './authClient';
import customRoutes from './customRoutes';

const App = () => (
  <Admin title="tinyauth" customRoutes={customRoutes} authClient={authClient} restClient={restClient}>
    <Resource name="users" list={UserList} create={UserCreate} edit={UserEdit} remove={Delete} icon={UserIcon} />
    <Resource name="groups" list={GroupList} create={GroupCreate} edit={GroupEdit} remove={Delete} icon={GroupIcon} />
  </Admin>
);

export default App;
