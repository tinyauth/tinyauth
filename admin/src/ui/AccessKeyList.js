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


class AccessKeyList extends Component {

  constructor(props) {
    super(props);

    this.state = {
      'isLoading': true,
      'keys': [],
    };
  }

  async componentWillMount() {
    try {
      const { user } = this.props;
      const response = await request('GET', `/users/${user}/keys`);
      this.setState({
        'isLoading': false,
        'keys': response.json,
      })
    } catch (e) {
      this.setState({'isLoading': false});
    }
  }

  renderInner() {
    const {isLoading, keys} = this.state;
    const { user } = this.props;

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
                 to={`/users/${user}/keys/${key.id}/delete`}
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
      <CardTitle title="Access Keys" />
      <CardText>{this.renderInner()}</CardText>
      <Toolbar>
          <ToolbarGroup>
            <RaisedButton
              label="Add Access Key"
              to={`/users/${user}/keys/add`}
              icon={<ContentAdd />}
              primary
             />
          </ToolbarGroup>
      </Toolbar>
    </Card>
  };

};

AccessKeyList.propTypes = {
  dispatch: PropTypes.func.isRequired,
};

export default connect()(AccessKeyList);
