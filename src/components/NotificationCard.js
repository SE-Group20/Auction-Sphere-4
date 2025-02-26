import { Link } from "react-router-dom";
import React from "react";
import axios from "axios";
import classes from '../css/NotificationCard.module.css';

const NotificationCard = props => {
  const { notif_id, image, message, detailPage, receivedTime } = props.data;

  const handleClick = async (e) => {
    try {
      await axios.put(`/notifications/${notif_id}/read`, {
        notif_id: notif_id
      });
    }
    catch (error) {
      console.error("Error marking notification as read:", error);
    } finally {
      window.location.href = detailPage; // Navigate after the request is done
    }
  }

  return (
    <Link to={detailPage} style={{ textDecoration: 'none', color: 'inherit' }}>

    <div className={classes.card} onClick={handleClick}>
      <div className={classes.content} >
          <div className={classes.image}>
            <img src={image} alt='Person ' />
          </div>

        <div className={classes.message}>

          <div className={classes.text}>{message}</div>
          <div className={classes.time}>{receivedTime}</div>
        </div>
      </div>
    </div>

    </Link>
  );
};
export default NotificationCard;
