import React from 'react';
import { List, Responsive, SimpleList, EditButton, DeleteButton, Datagrid, TextField } from 'admin-on-rest/lib/mui';

export const GroupList = (props) => (
  <List {...props}>
    <Responsive
      small={
        <SimpleList
          primaryText={record => record.name}
        />
      }
      medium={<Datagrid>
          <TextField label="Group" source="name" />
          <EditButton />
          <DeleteButton />
        </Datagrid>
      }
      />
  </List>
);
