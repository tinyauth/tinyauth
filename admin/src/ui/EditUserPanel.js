import React, { Component } from 'react';
import { connect } from 'react-redux';

import { Card, CardText } from 'material-ui/Card';
import ActionCheck from 'material-ui/svg-icons/action/check-circle';
import RaisedButton from 'material-ui/RaisedButton';
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

import TextField from 'material-ui/TextField';

import { ViewTitle } from 'admin-on-rest';
import { showNotification } from 'admin-on-rest';
import { crudGetOne as crudGetOneAction } from 'admin-on-rest/lib/actions/dataActions';

import PropTypes from 'prop-types';

import { request } from '../restClient';


class EditUserPanel extends Component {
    constructor(props) {
        super(props);

        this.state = {
          'id': '',
          'username': '',
          'isLoading': true,
          'submitting': false,
          'pristine': true,
        };

        this.handleAddUserToGroup = this.handleAddUserToGroup.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
    }

    async componentWillMount() {
      try {
        const { user } = this.props;

        const response = await request('GET', `/users/${user}`);
        this.setState({
          'isLoading': false,
          'id': response.json.id,
          'username': response.json.username,
        })
      } catch (e) {
        this.setState({'isLoading': false});
      }
    }

    async handleAddUserToGroup(event) {
      const { dispatch, user } = this.props;
      const { username } = this.state;

      this.setState({'submitting': true});

      try {
        let { status } = await request('PUT', `/users/${user}`, {
          username: username,
        });

        if (status === 200) {
          // Let the user know it worked
          dispatch(showNotification("Saved user"));
          dispatch(crudGetOneAction("users", user));
        } else {
          dispatch(showNotification("Unhandled server error. Please try again laster."));
        }
      }
      finally {
        this.setState({
          'submitting': false,
          'pristine': true,
        })
      }
    }

    handleCancel() {
        this.props.history.goBack();
    }

    render() {
      return <Card style={{marginBottom: "20px"}}>
          <ViewTitle title="Edit User" />
          <CardText>
              <TextField
                floatingLabelText="Name"
                hintText="Name"
                errorText=""
                value={this.state.username}
                onChange={ev => this.setState({username: ev.target.value, pristine: false})}
                />
          </CardText>
          <Toolbar>
              <ToolbarGroup>
                  <RaisedButton
                      type="submit"
                      label="Save"
                      icon={<ActionCheck />}
                      onClick={this.handleAddUserToGroup}
                      disabled={this.state.submitting || this.state.pristine}
                      primary
                  />
              </ToolbarGroup>
          </Toolbar>
      </Card>
    };
};

EditUserPanel.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(EditUserPanel);
