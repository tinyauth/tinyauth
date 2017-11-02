import React from 'react';
import { List, Responsive, SimpleList, Create, Edit, EditButton, DeleteButton, SimpleForm, Datagrid, TextField, DisabledInput, TextInput, ReferenceManyField } from 'admin-on-rest/lib/mui';

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

export const UserEdit = (props) => (
  <Edit title={<UserTitle />} {...props}>
    <SimpleForm>
      <DisabledInput source="id" />
      <TextInput source="username" validation={{ required: true }} />
      <ReferenceManyField label="Groups" reference="groups" target="users">
        <Datagrid>
            <TextField source="name" />
            <EditButton />
        </Datagrid>
      </ReferenceManyField>

    </SimpleForm>
  </Edit>
);

export const UserCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="username" validation={{ required: true }} />
    </SimpleForm>
  </Create>
);
