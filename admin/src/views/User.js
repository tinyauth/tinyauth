import React from 'react';
import { List, Responsive, SimpleList, Create, Edit, EditButton, DeleteButton, SimpleForm, Datagrid, TextField, DisabledInput, TextInput, ReferenceArrayField, ReferenceArrayInput, SelectArrayInput, SingleFieldList, ChipField } from 'admin-on-rest/lib/mui';

import {TabbedForm} from 'admin-on-rest/lib/mui';
import {FormTab} from 'admin-on-rest/lib/mui';

import AddUserToGroupButton from '../ui/AddUserToGroupButton';
import { CardActions } from 'material-ui/Card';
import { ListButton } from 'admin-on-rest/lib/mui';


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
      <TabbedForm defaultValue={{ role: 'user' }}>
          <FormTab label="Summary">
              <DisabledInput source="id" />
              <TextInput label="Username" source="username" validation={{ required: true }} />
          </FormTab>
          <FormTab label="Groups">
          <ReferenceArrayField label="" source="groups" reference="groups">
              <Datagrid sort={{ field: 'name', order: 'DESC' }}>
                  <TextField label="Group Name" source="name" />
                  <EditButton />
              </Datagrid>
          </ReferenceArrayField>
          </FormTab>
      </TabbedForm>
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
