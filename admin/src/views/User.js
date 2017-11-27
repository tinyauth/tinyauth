import React from 'react';
import { List, Responsive, SimpleList, EditButton, DeleteButton, Datagrid, TextField, FunctionField } from 'admin-on-rest/lib/mui';

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
