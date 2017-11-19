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
import {
  Card,
  CardTitle,
  CardText,
} from 'material-ui/Card'
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

import ContentAdd from 'material-ui/svg-icons/content/add';
import ButtonIcon from 'material-ui/svg-icons/av/playlist-add';
import GenericButton from './GenericButton';
import RaisedButton from './RaisedButton';
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
      const { user } = this.props;
      const response = await request('GET', `/users/${user}/policies`);
      this.setState({
        'isLoading': false,
        'policies': response.json,
      })
    } catch (e) {
      this.setState({'isLoading': false});
    }
  }

  renderInner() {
    const {isLoading, policies} = this.state;
    const { user } = this.props;

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
                to={`/users/${user}/policies/${policy.id}/edit`}
                icon={<ButtonIcon />}
               />
               <GenericButton
                 label="Delete"
                 to={`/users/${user}/policies/${policy.id}/delete`}
                 icon={<ButtonIcon />}
                />
            </TableRowColumn>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  };

  render() {
    const { user } = this.props;

    return <Card style={{marginBottom: "20px"}}>
      <CardTitle title="Policies" />
      <CardText>{this.renderInner()}</CardText>
      <Toolbar>
          <ToolbarGroup>
            <RaisedButton
              label="Add policy"
              to={`/users/${user}/policies/add`}
              icon={<ContentAdd />}
              primary
             />
          </ToolbarGroup>
      </Toolbar>
    </Card>
  };
};

PolicyList.propTypes = {
  dispatch: PropTypes.func.isRequired,
};

export default connect()(PolicyList);
