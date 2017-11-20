import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import FlatButton from 'material-ui/FlatButton';

const GenericButton = ({label, to, icon, primary=false}) => (
  <FlatButton
    label={label}
    icon={icon}
    containerElement={
      <Link to={to} />
    }
    primary={primary}
    style={{ overflow: 'inherit' }}
  />
);

GenericButton.propTypes = {
  label: PropTypes.string,
  to: PropTypes.string,
};

export default GenericButton;
