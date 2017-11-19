import React, { Component } from 'react';
import { connect } from 'react-redux';

import { Card, CardText } from 'material-ui/Card';
import ActionCheck from 'material-ui/svg-icons/action/check-circle';
import AlertError from 'material-ui/svg-icons/alert/error-outline';
import RaisedButton from 'material-ui/RaisedButton';
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

import TextField from 'material-ui/TextField';

import { ViewTitle } from 'admin-on-rest';
import { showNotification } from 'admin-on-rest';

import PropTypes from 'prop-types';

import { request } from '../restClient';

const policyEditorStyle = {
  fontFamily: 'Menlo, Courier New, Mono',
}

class AddAccessKey extends Component {
    constructor(props) {
        super(props);
        this.handleRequestAccessKey = this.handleRequestAccessKey.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
    }

    getBasePath() {
        const { location } = this.props;
        return location.pathname
            .split('/')
            .slice(0, -1)
            .join('/');
    }

    componentWillMount() {
      this.setState({
        'generated': false,
        'access_key_id': '',
        'secret_access_key': '',
        'submitting': false,
      });
    }

    async handleRequestAccessKey(event) {
      const { dispatch } = this.props;
      const user = this.props.match.params.user;

      this.setState({'submitting': true});

      try {
        let { status, json } = await request('POST', `/users/${user}/keys`);

        if (status === 200) {
          this.setState({
            access_key_id: json.access_key_id,
            secret_access_key: json.secret_access_key,
            generated: true,
          })

          // Let the user know it worked
          dispatch(showNotification("Key created"));
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
          <ViewTitle title="Add Access Key" />
          <CardText>
              <TextField
                floatingLabelText="Access Key Id"
                hintText="Access Key Id"
                value={this.state.access_key_id}
                />

                <br />

                <TextField
                  inputStyle={policyEditorStyle}
                  floatingLabelText="Secret Access Key"
                  hintText="Secret Access Key"
                  value={this.state.secret_access_key}
                  />
          </CardText>
          <Toolbar>
              <ToolbarGroup>
                  <RaisedButton
                      type="submit"
                      label="Generate Key"
                      icon={<ActionCheck />}
                      onClick={this.handleRequestAccessKey}
                      disabled={this.state.generated || this.state.submitting}
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

AddAccessKey.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(AddAccessKey);
