import React from 'react';

import { Admin, Resource } from 'admin-on-rest';

import UserIcon from 'material-ui/svg-icons/social/person';
import GroupIcon from 'material-ui/svg-icons/social/group';

import { UserList } from './views/User';
import { GroupList } from './views/Group';

import restClient from './restClient';
import authClient from './authClient';
import customRoutes from './customRoutes';

const App = () => (
  <Admin title="tinyauth" customRoutes={customRoutes} authClient={authClient} restClient={restClient}>
    <Resource name="users" create={true} list={UserList} icon={UserIcon} />
    <Resource name="groups" create={true} list={GroupList}icon={GroupIcon} />
  </Admin>
);

export default App;
