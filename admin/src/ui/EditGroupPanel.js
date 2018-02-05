import React, { Component } from 'react';
import { connect } from 'react-redux';
import { push } from 'react-router-redux';

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


class EditGroupPanel extends Component {
    constructor(props) {
        super(props);

        this.state = {
          'id': '',
          'name': '',
          'isLoading': true,
          'submitting': false,
          'pristine': true,
        };

        this.handleEditGroup = this.handleEditGroup.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
    }

    async componentWillMount() {
      try {
        const { group } = this.props;

        const response = await request('GET', `/groups/${group}`);
        this.setState({
          'isLoading': false,
          'id': response.json.id,
          'name': response.json.name,
        })
      } catch (e) {
        this.setState({'isLoading': false});
      }
    }

    async handleEditGroup(event) {
      const { dispatch, group } = this.props;
      const { name } = this.state;

      this.setState({'submitting': true});

      try {
        let { status, json } = await request('PUT', `/groups/${group}`, {
          name: name,
        });

        if (status === 200) {
          // Let the user know it worked
          dispatch(showNotification("Saved group"));
          dispatch(crudGetOneAction("groups", json['id']));

          // This save caused id to change - redirect to self
          if (json['id'] !== group) {
            dispatch(push('/groups/' + json['id']));
          }

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
          <ViewTitle title="Edit Group" />
          <CardText>
              <TextField
                floatingLabelText="Name"
                hintText="Name"
                errorText=""
                value={this.state.name}
                onChange={ev => this.setState({name: ev.target.value, pristine: false})}
                />
          </CardText>
          <Toolbar>
              <ToolbarGroup>
                  <RaisedButton
                      type="submit"
                      label="Save"
                      icon={<ActionCheck />}
                      onClick={this.handleEditGroup}
                      disabled={this.state.submitting || this.state.pristine}
                      primary
                  />
              </ToolbarGroup>
          </Toolbar>
      </Card>
    };
};

EditGroupPanel.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(EditGroupPanel);
