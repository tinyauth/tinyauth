import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import { Card, CardText } from 'material-ui/Card';
import ActionCheck from 'material-ui/svg-icons/action/check-circle';
import RaisedButton from 'material-ui/RaisedButton';
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

import TextField from 'material-ui/TextField';

import { ViewTitle } from 'admin-on-rest';
import { showNotification } from 'admin-on-rest';
import { push } from 'react-router-redux';
import { crudGetOne as crudGetOneAction } from 'admin-on-rest/lib/actions/dataActions';

import { request } from '../restClient';


class CreateUser extends Component {
  constructor(props) {
      super(props);

      this.state = {
        'id': '',
        'username': '',
        'password': '',
        'isLoading': true,
        'submitting': false,
        'pristine': true,
      };

      this.handleCreateUser = this.handleCreateUser.bind(this);
      this.handleCancel = this.handleCancel.bind(this);
  }

  async handleCreateUser(event) {
    const { dispatch } = this.props;
    const { username, password } = this.state;

    this.setState({'submitting': true});

    try {
      let { status, json } = await request('POST', "/users", {
        username: username,
        password: password,
      });

      if (status === 200) {
        // Let the user know it worked
        dispatch(showNotification("Saved user"));
        dispatch(crudGetOneAction("users", json.id));
        dispatch(push(`/users/${json.id}`));

      } else {
        dispatch(showNotification("Unhandled server error. Please try again later."));
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
        <ViewTitle title="Add New User" />
        <CardText>
            <TextField
              floatingLabelText="Name"
              hintText="Name"
              errorText=""
              value={this.state.username}
              onChange={ev => this.setState({username: ev.target.value, pristine: false})}
              />

            <br />

            <TextField
              floatingLabelText="Password"
              hintText="Password"
              errorText=""
              type="password"
              value={this.state.password}
              onChange={ev => this.setState({password: ev.target.value, pristine: false})}
              />
        </CardText>
        <Toolbar>
            <ToolbarGroup>
                <RaisedButton
                    type="submit"
                    label="Save"
                    icon={<ActionCheck />}
                    onClick={this.handleCreateUser}
                    disabled={this.state.submitting || this.state.pristine}
                    primary
                />
            </ToolbarGroup>
        </Toolbar>
    </Card>
  };
};

CreateUser.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(CreateUser);
