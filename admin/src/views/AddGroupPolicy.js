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
import { push } from 'react-router-redux';

import PropTypes from 'prop-types';

import { request } from '../restClient';

const policyEditorStyle = {
  fontFamily: 'Menlo, Courier New, Mono',
}

class AddGroupPolicy extends Component {
    constructor(props) {
        super(props);
        this.handleAddPolicyToGroup = this.handleAddPolicyToGroup.bind(this);
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
        'id': '',
        'name': '',
        'policy': '',
        'isLoading': false,
        'submitting': false,
        'pristine': true,
      });
    }

    async handleAddPolicyToGroup(event) {
      const { dispatch } = this.props;
      const { group } = this.props.match.params;

      const {name, policy} = this.state;

      this.setState({'submitting': true});

      try {
        let { status } = await request('POST', `/groups/${group}/policies`, {
          name: name,
          policy: policy
        });

        if (status === 200) {
          // Let the user know it worked
          dispatch(showNotification("Saved policy"));

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
          <ViewTitle title="Add Policy" />
          <CardText>
              <TextField
                floatingLabelText="Name"
                hintText="Name"
                errorText=""
                value={this.state.name}
                onChange={ev => this.setState({name: ev.target.value, pristine: false})}
                />

                <br />

                <TextField
                  inputStyle={policyEditorStyle}
                  floatingLabelText="Policy"
                  hintText="Policy"
                  errorText=""
                  value={this.state.policy}
                  onChange={ev => this.setState({policy: ev.target.value, pristine: false})}
                  multiLine={true}
                  fullWidth={true}
                  rows={10}
                  />
          </CardText>
          <Toolbar>
              <ToolbarGroup>
                  <RaisedButton
                      type="submit"
                      label="Save"
                      icon={<ActionCheck />}
                      onClick={this.handleAddPolicyToGroup}
                      disabled={this.state.submitting || this.state.pristine}
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

AddGroupPolicy.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(AddGroupPolicy);
