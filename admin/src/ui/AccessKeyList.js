import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import {
  Table,
  TableBody,
  TableHeader,
  TableHeaderColumn,
  TableRow,
  TableRowColumn,
} from 'material-ui/Table';

import ButtonIcon from 'material-ui/svg-icons/av/playlist-add';
import GenericButton from './GenericButton'
import { request } from '../restClient';


class keyList extends Component {

  constructor(props) {
    super(props);

    this.state = {
      'isLoading': true,
      'keys': [],
    };
  }

  async componentWillMount() {
    try {
      const response = await request('GET', '/users/1/keys');
      this.setState({
        'isLoading': false,
        'keys': response.json,
      })
    } catch (e) {
      this.setState({'isLoading': false});
    }
  }

  render() {
    const {isLoading, keys} = this.state;

    if (isLoading) {
      return <div>Loading...</div>;
    }

    if (keys.length === 0) {
      return <div>There are no keys attached to this user or you do not have permission to view them</div>;
    }

    return <Table selectable={false}>
      <TableHeader displaySelectAll={false}>
        <TableRow>
          <TableHeaderColumn>Access Key Id</TableHeaderColumn>
          <TableHeaderColumn>Actions</TableHeaderColumn>
        </TableRow>
      </TableHeader>
      <TableBody displayRowCheckbox={false}>
        {keys.map((key) => (
          <TableRow key={key.access_key_id}>
            <TableRowColumn>{key.access_key_id}</TableRowColumn>
            <TableRowColumn>
               <GenericButton
                 label="Delete"
                 to={`/users/1/keys/${key.id}/delete`}
                 icon={<ButtonIcon />}
                />
            </TableRowColumn>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  };
};

keyList.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(keyList);
