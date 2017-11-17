import React from 'react';
import { List, Responsive, SimpleList, Create, Edit, EditButton, DeleteButton, SimpleForm, Datagrid, TextField, DisabledInput, TextInput,  ReferenceArrayField, ReferenceArrayInput, SelectArrayInput, SingleFieldList, ChipField } from 'admin-on-rest/lib/mui';

import AddUserToGroupButton from '../ui/AddUserToGroupButton';
import { CardActions } from 'material-ui/Card';
import { ListButton } from 'admin-on-rest/lib/mui';

import PolicyList from '../ui/PolicyList';
import AccessKeyList from '../ui/AccessKeyList';


export const UserList = (props) => (
  <List {...props}>
    <Responsive
      small={
        <SimpleList
          primaryText={record => record.username}
        />
      }
      medium={<Datagrid>
          <TextField label="Username" source="username" />
          <ReferenceArrayField label="Groups" reference="groups" source="groups">
              <SingleFieldList>
                  <ChipField source="name" />
              </SingleFieldList>
          </ReferenceArrayField>
          <EditButton />
          <DeleteButton />
        </Datagrid>
      }
      />
  </List>
);

const UserTitle = ({ record }) => {
    return <span>User {record ? `"${record.username}"` : ''}</span>;
};

const UserEditActions = ({ basePath, data }) => (
    <CardActions>
        <ListButton basePath={basePath} />
        <AddUserToGroupButton basePath={basePath} record={data} />
        <DeleteButton basePath={basePath} record={data} />
    </CardActions>
);

export const UserEdit = (props) => (
  <Edit title={<UserTitle />} actions={<UserEditActions />} {...props}>
  {permissions => (
      <SimpleForm>
        <h1>User Details</h1>
        <DisabledInput source="id" />
        <TextInput label="Username" source="username" validation={{ required: true }} />

        <h1>Access Keys</h1>
        <AccessKeyList />

        <h1>Groups</h1>
        <ReferenceArrayField label="" source="groups" reference="groups">
          <Datagrid sort={{ field: 'name', order: 'DESC' }}>
            <TextField label="Group Name" source="name" />
            <EditButton />
          </Datagrid>
        </ReferenceArrayField>

        <h1>Policies</h1>
        <PolicyList />
      </SimpleForm>
  )}
  </Edit>
);

export const UserCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="username" validation={{ required: true }} />

      <ReferenceArrayInput label="Groups" source="groups" reference="groups" allowEmpty>
          <SelectArrayInput optionText="name"/>
      </ReferenceArrayInput>
    </SimpleForm>
  </Create>
);
