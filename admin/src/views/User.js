import React from 'react';
import { List, Responsive, SimpleList, Create, Edit, EditButton, DeleteButton, SimpleForm, Datagrid, TextField, DisabledInput, TextInput, ReferenceArrayField, ReferenceArrayInput, SelectArrayInput, SingleFieldList, ChipField } from 'admin-on-rest/lib/mui';

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

export const UserEdit = (props) => (
  <Edit title={<UserTitle />} {...props}>
    <SimpleForm>
      <DisabledInput source="id" />
      <TextInput label="Username" source="username" validation={{ required: true }} />
      <ReferenceArrayInput label="Groups" source="groups" reference="groups" allowEmpty>
        <SelectArrayInput optionText="name" />
      </ReferenceArrayInput>
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
