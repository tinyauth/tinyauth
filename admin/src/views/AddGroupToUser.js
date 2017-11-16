import React, { Component } from 'react';

import { Card, CardText, CardActions } from 'material-ui/Card';
import ActionCheck from 'material-ui/svg-icons/action/check-circle';
import AlertError from 'material-ui/svg-icons/alert/error-outline';
import RaisedButton from 'material-ui/RaisedButton';
import { Toolbar, ToolbarGroup } from 'material-ui/Toolbar';

import ChipInput from 'material-ui-chip-input'

import { ViewTitle } from 'admin-on-rest';
import { crudGetOne as crudGetOneAction } from 'admin-on-rest/lib/actions/dataActions';


class AddGroupToUser extends Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.goBack = this.goBack.bind(this);
    }

    getBasePath() {
        const { location } = this.props;
        return location.pathname
            .split('/')
            .slice(0, -2)
            .join('/');
    }

    handleSubmit(event) {
        event.preventDefault();

        const token = window.btoa(localStorage.getItem('token'));

        var headers = new Headers({
          Accept: 'application/json',
          Authorization: `Basic ${token}`,
        });

        console.log(this.props);
        var d = fetch(
          `http://localhost:8000/api/v1/groups/1/add-user`,
          {
            method: "POST",
            headers: headers,
            body: JSON.stringify({
              'user': this.props.match.params.user,
            }) 
          }
        )
        
        d.then(response => response.json()).then(json => console.log(json));
        // .then(json => dispatch(crudGetOneAction("users", this.props.match.params.user, this.getBasePath())));
        console.log('Done');
    }

    goBack() {
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
                      onClick={this.handleSubmit}
                      primary
                  />
                  <RaisedButton
                      label="Cancel"
                      icon={<AlertError />}
                      onClick={this.goBack}
                  />
              </ToolbarGroup>
          </Toolbar>
      </Card>
    };
};

export default AddGroupToUser;
