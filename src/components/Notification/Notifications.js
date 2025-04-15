import React, { Component } from 'react';
import PropTypes from 'prop-types';

class Notifications extends Component {
    constructor(props) {
        super(props);
    }

    // debugging: print new props on creation and update
    componentDidMount() {
        console.log('Notifications component mounted with props:', this.props);
    }
    componentDidUpdate(prevProps) {
        if (prevProps.data !== this.props.data) {
            console.log('Notifications component updated with new props:', this.props);
        }
    }

    render() {
        const { data } = this.props;
        return (
            <div id="notifications">{data.length}</div>
        );
    }
}

Notifications.propTypes = {
    data: PropTypes.array.isRequired,
};

export default Notifications;