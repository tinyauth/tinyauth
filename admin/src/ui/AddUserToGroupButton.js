import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import FlatButton from 'material-ui/FlatButton';
import ButtonIcon from 'material-ui/svg-icons/av/playlist-add';
import linkToRecord from 'admin-on-rest/lib/util/linkToRecord';

const AddUserToGroupButton = ({
    basePath = '',
    label = 'Add To Group',
    record = {},
    translate,
}) => (
    <FlatButton
        label={label}
        icon={<ButtonIcon />}
        containerElement={
            <Link to={`${linkToRecord(basePath, record.id)}/add-to-group`} />
        }
        style={{ overflow: 'inherit' }}
    />
);

AddUserToGroupButton.propTypes = {
    basePath: PropTypes.string,
    label: PropTypes.string,
    record: PropTypes.object,
};

export default AddUserToGroupButton;
