import React from 'react';
import { List, Responsive, SimpleList, Create, Edit, EditButton, DeleteButton, SimpleForm, Datagrid, TextField, DisabledInput, TextInput } from 'admin-on-rest/lib/mui';

export const GroupList = (props) => (
  <List {...props}>
    <Responsive
      small={
        <SimpleList
          primaryText={record => record.name}
        />
      }
      medium={<Datagrid>
          <TextField label="Groupname" source="name" />
          <EditButton />
          <DeleteButton />
        </Datagrid>
      }
      />
  </List>
);

const GroupTitle = ({ record }) => {
    return <span>Group {record ? `"${record.name}"` : ''}</span>;
};

export const GroupEdit = (props) => (
  <Edit title={<GroupTitle />} {...props}>
    <SimpleForm>
      <DisabledInput source="id" />
      <TextInput source="name" validation={{ required: true }} />
    </SimpleForm>
  </Edit>
);

export const GroupCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="name" validation={{ required: true }} />
    </SimpleForm>
  </Create>
);
