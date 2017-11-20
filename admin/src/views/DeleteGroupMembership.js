import React, { Component } from 'react';
import { connect } from 'react-redux';

import { Card, CardText } from 'material-ui/Card';
import ActionCheck from 'material-ui/svg-icons/action/check-circle';
import AlertError from 'material-ui/svg-icons/alert/error-outline';
import RaisedButton from 'material-ui/RaisedButton';
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

import { ViewTitle } from 'admin-on-rest';
import { showNotification } from 'admin-on-rest';
import { push } from 'react-router-redux';

import PropTypes from 'prop-types';

import { request } from '../restClient';


class DeleteGroupMembership extends Component {
    constructor(props) {
        super(props);

        this.state = {
          'submitting': false,
        };

        this.handleDeleteGroupMembership = this.handleDeleteGroupMembership.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
    }

    getBasePath() {
        const { location } = this.props;
        return location.pathname
            .split('/')
            .slice(0, -3)
            .join('/');
    }

    async handleDeleteGroupMembership(event) {
      const { dispatch } = this.props;
      const { group, user } = this.props.match.params;

      this.setState({'submitting': true});

      try {
        let { status } = await request('DELETE', `/groups/${group}/users/${user}`);

        if (status === 201) {
          // Let the user know it worked
          dispatch(showNotification("Removed user from group"));

          // Bounce back to the user detail view
          dispatch(push(this.getBasePath()));
        } else {
          dispatch(showNotification("Unhandled server error. Please try again laster."));
        }
      }
      finally {
        this.setState({'submitting': false})
      }
    }

    handleCancel() {
        this.props.history.goBack();
    }

    render() {
      return <Card>
          <ViewTitle title="Remove user from group" />
          <CardText>Are you sure you want to remove the user from this group?</CardText>
          <Toolbar>
              <ToolbarGroup>
                  <RaisedButton
                      type="submit"
                      label="Remove"
                      icon={<ActionCheck />}
                      onClick={this.handleDeleteGroupMembership}
                      disabled={this.state.submitting}
                      primary
                  />
                  <RaisedButton
                      label="Cancel"
                      icon={<AlertError />}
                      disabled={this.state.submitting}
                      onClick={this.handleCancel}
                  />
              </ToolbarGroup>
          </Toolbar>
      </Card>
    };
};

DeleteGroupMembership.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(DeleteGroupMembership);
