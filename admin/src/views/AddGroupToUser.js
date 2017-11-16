import React, { Component } from 'react';
import { connect } from 'react-redux';

import { Card, CardText } from 'material-ui/Card';
import ActionCheck from 'material-ui/svg-icons/action/check-circle';
import AlertError from 'material-ui/svg-icons/alert/error-outline';
import RaisedButton from 'material-ui/RaisedButton';
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

import ChipInput from 'material-ui-chip-input'

import { ViewTitle } from 'admin-on-rest';
import { crudGetOne as crudGetOneAction } from 'admin-on-rest/lib/actions/dataActions';
import { showNotification } from 'admin-on-rest';
import { push } from 'react-router-redux';

import PropTypes from 'prop-types';

import { request } from '../restClient';


class AddGroupToUser extends Component {
    constructor(props) {
        super(props);
        this.handleAddUserToGroup = this.handleAddUserToGroup.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
    }

    getBasePath() {
        const { location } = this.props;
        return location.pathname
            .split('/')
            .slice(0, -1)
            .join('/');
    }

    handleAddUserToGroup(event) {
        const { dispatch } = this.props;
        const group = 1;
        const user = this.props.match.params.user;

        request('POST', `/groups/${group}/add-user`, {user: user})
          .then(res => dispatch(crudGetOneAction("users", user)))
          .then(res => dispatch(crudGetOneAction("groups", group)))
          .then(res => dispatch(showNotification("User added to group")))
          .then(res => dispatch(push(this.getBasePath())));
    }

    handleCancel() {
        this.props.history.goBack();
    }

    render() {
      return <Card>
          <ViewTitle title="Add User To Group" />
          <CardText>
              <ChipInput defaultValue={['foo', 'bar']}/>
          </CardText>
          <Toolbar>
              <ToolbarGroup>
                  <RaisedButton
                      type="submit"
                      label="Add"
                      icon={<ActionCheck />}
                      onClick={this.handleAddUserToGroup}
                      primary
                  />
                  <RaisedButton
                      label="Cancel"
                      icon={<AlertError />}
                      onClick={this.handleCancel}
                  />
              </ToolbarGroup>
          </Toolbar>
      </Card>
    };
};

AddGroupToUser.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(AddGroupToUser);
