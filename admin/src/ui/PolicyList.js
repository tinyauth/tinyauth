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


class PolicyList extends Component {

  constructor(props) {
    super(props);

    this.state = {
      'isLoading': true,
      'policies': [],
    };
  }
  
  async componentWillMount() {
    try {
      const response = await request('GET', '/users/1/policies');
      this.setState({
        'isLoading': false,
        'policies': response.json,
      })
    } catch (e) {
      this.setState({'isLoading': false});
    }
  }

  render() {
    const {isLoading, policies} = this.state;
    
    if (isLoading) {
      return <div>Loading...</div>;
    }
    
    if (policies.length === 0) {
      return <div>There are no policies attached to this user or you do not have permission to view them</div>;
    }

    return <Table selectable={false}>
      <TableHeader displaySelectAll={false}>
        <TableRow>
          <TableHeaderColumn>Name</TableHeaderColumn>
          <TableHeaderColumn>Actions</TableHeaderColumn>
        </TableRow>
      </TableHeader>
      <TableBody displayRowCheckbox={false}>
        {policies.map((policy) => (
          <TableRow key={policy.name}>
            <TableRowColumn>{policy.name}</TableRowColumn>
            <TableRowColumn>
              <GenericButton
                label="Edit"
                to={`/users/1/policies/${policy.id}/edit`}
                icon={<ButtonIcon />}
               />
               <GenericButton
                 label="Delete"
                 to={`/users/1/policies/${policy.id}/delete`}
                 icon={<ButtonIcon />}
                />
            </TableRowColumn>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  };
};

PolicyList.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(PolicyList);
