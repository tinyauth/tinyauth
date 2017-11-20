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


class CreateGroup extends Component {
  constructor(props) {
      super(props);

      this.state = {
        'id': '',
        'name': '',
        'isLoading': true,
        'submitting': false,
        'pristine': true,
      };

      this.handleCreateGroup = this.handleCreateGroup.bind(this);
      this.handleCancel = this.handleCancel.bind(this);
  }

  async handleCreateGroup(event) {
    const { dispatch } = this.props;
    const { name } = this.state;

    this.setState({'submitting': true});

    try {
      let { status, json } = await request('POST', "/groups", {
        name: name,
      });

      if (status === 200) {
        // Let the group know it worked
        dispatch(showNotification("Saved group"));
        dispatch(crudGetOneAction("groups", json.id));
        dispatch(push(`/groups/${json.id}`));

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
        <ViewTitle title="Create Group" />
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
                    onClick={this.handleCreateGroup}
                    disabled={this.state.submitting || this.state.pristine}
                    primary
                />
            </ToolbarGroup>
        </Toolbar>
    </Card>
  };
};

CreateGroup.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(CreateGroup);
