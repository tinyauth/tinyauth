import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';

import EditGroupPanel from '../ui/EditGroupPanel';
import GroupPolicyList from '../ui/GroupPolicyList';


class EditGroup extends Component {
    render() {
      const { group } = this.props.match.params;

      return <div>
        <EditGroupPanel group={group} />
        <GroupPolicyList group={group} />
      </div>
    };
};

EditGroup.propTypes = {
    dispatch: PropTypes.func.isRequired,
};

export default connect()(EditGroup);
