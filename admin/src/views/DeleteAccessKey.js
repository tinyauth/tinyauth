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


class DeleteAccessKey extends Component {
    constructor(props) {
        super(props);

        this.state = {
          'submitting': false,
        };

        this.handleDeleteAccessKey = this.handleDeleteAccessKey.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
    }

    getBasePath() {
        const { location } = this.props;
        return location.pathname
            .split('/')
            .slice(0, -3)
            .join('/');
    }

    async handleDeleteAccessKey(event) {
      const { dispatch } = this.props;
      const { user, key } = this.props.match.params;

      this.setState({'submitting': true});

      try {
        let { status } = await request('DELETE', `/users/${user}/keys/${key}`);

        if (status === 201) {
          // Let the user know it worked
          dispatch(showNotification("Removed access key"));

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
          <ViewTitle title="Remove access mey from user" />
          <CardText>Are you sure you want to remove this access key?</CardText>
          <Toolbar>
              <ToolbarGroup>
                  <RaisedButton
                      type="submit"
                      label="Delete"
                      icon={<ActionCheck />}
                      onClick={this.handleDeleteAccessKey}
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

DeleteAccessKey.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(DeleteAccessKey);
