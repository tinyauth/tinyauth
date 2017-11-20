import React from 'react';
import { List, Responsive, SimpleList, Create, EditButton, DeleteButton, SimpleForm, Datagrid, TextField, TextInput, ReferenceArrayInput, SelectArrayInput, FunctionField } from 'admin-on-rest/lib/mui';

import { Chip } from 'material-ui';

const styles = {
  chip: {
    margin: 4,
  },
  wrapper: {
    display: 'flex',
    flexWrap: 'wrap',
  },
};

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
          <FunctionField
            label="Groups"
            source="groups"
            render={ record => <div style={styles.wrapper}>{record.groups.map(group => <Chip style={styles.wrapper} key={group.id}>{group.name}</Chip>)}</div> }
          />
          <EditButton />
          <DeleteButton />
        </Datagrid>
      }
      />
  </List>
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
