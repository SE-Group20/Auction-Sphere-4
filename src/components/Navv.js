import React, { useState, useEffect } from 'react'
import { toast } from 'react-toastify'
import axios from 'axios'
import {
    Collapse,
    Navbar,
    NavbarToggler,
    NavbarBrand,
    Nav,
    NavItem,
    NavLink,
    UncontrolledDropdown,
    DropdownToggle,
    DropdownMenu,
    DropdownItem,
    NavbarText,
} from 'reactstrap'
import Notifications from "react-notifications-menu"
// import Notifications from './Notification/Notifications'
import NotificationCard from './NotificationCard'
import notifLogo from '../assets/logo24.png'
import logo from '../assets/NavLogo.png'

/**
 * This component is the Navigation bar of our application.
 */

function Navv(args) {
    const [isOpen, setIsOpen] = useState(true)
    const [notifications, setNotifications] = useState([]);
    
    const toggle = () => setIsOpen(!isOpen)
    const handleLogout = () => {
        localStorage.clear()
        window.location.reload()
        toast.info('Logged out')
    }
    
    /**
     * This function fetchs all notifications for the current user
     * Uses global id in app.py to get current user
     */
    const fetchNotifications = async () => {
        try {
            const response = await axios.get(`/notifications/get`);
            // setNotifications(response.data.notifications);
            // convert from string to json before setting state
            console.log("Notifications", notifications)
        } catch (error) {
            console.error("Error fetching notifications:", error);
        }
    };

    /**
     * This function marks all notifications for the current user as read
     */
    const markAllAsRead = async () => {
        try {
          const response = await axios.put(`/notifications/read`) 
          console.log('All notifications marked as read:', response.data);
        } catch (error) {
          console.error('Failed to mark notifications as read:', error);
        }
      };

    /**
     * This function featchesall notifications for the current user
     * Every 10 seconds, or initially
     */
    useEffect(() => {
        fetchNotifications(); 

        const interval = setInterval(() => {
            fetchNotifications(); // Poll every 10s
        }, 10000);

        return () => clearInterval(interval);
    }, []);
    

    return (
        <div>
            <Navbar
                style={{
                    marginBottom: '1rem',
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    left: 0,
                }}
                color="dark"
                light
                expand="md"
            >
                <NavbarBrand href="/">
                    <img
                        src={logo}
                        style={{
                            height: 40,
                            width: 60,
                        }}
                    />
                </NavbarBrand>
                <NavbarToggler
                    onClick={() => {
                        setIsOpen(!isOpen)
                    }}
                />

                <Collapse isOpen={isOpen} navbar>
                    <Nav navbar>
                        <NavItem>
                            <NavLink
                                href="/products"
                                style={{ color: 'white' }}
                            >
                                Products
                            </NavLink>
                        </NavItem>
                        {localStorage.getItem('auth') === 'true' ? (
                            <>
                                <NavItem>
                                    <NavLink
                                        href="/sell"
                                        style={{ color: 'white' }}
                                    >
                                        Sell
                                    </NavLink>
                                </NavItem>
                                <NavItem>
                                    <NavLink
                                        href="/messages"
                                        style={{ color: 'white' }}
                                    >
                                        Messages
                                    </NavLink>
                                </NavItem>
                                <NavItem>
                                    <NavLink
                                        style={{ color: 'white' }}
                                        href="/"
                                        onClick={handleLogout}
                                    >
                                        Logout
                                    </NavLink>
                                </NavItem>
                                    <NavItem>
                                        <NavLink href="/profile" style={{ color: 'white' }}>
                                            Profile
                                        </NavLink>
                                    </NavItem>
                                <NavItem>
                                    <NavLink
                                        href="/watchlist"
                                        style={{ color: 'white' }}
                                    >
                                        Watchlist
                                    </NavLink>
                                </NavItem>
                                    
                        </>
                        ) : (
                            <>
                                <NavItem className="float-right">
                                    <NavLink
                                        href="/login"
                                        style={{ color: 'white' }}
                                    >
                                        Login
                                    </NavLink>
                                </NavItem>
                                <NavItem>
                                    <NavLink
                                        href="/signup"
                                        style={{ color: 'white' }}
                                    >
                                        Signup
                                    </NavLink>
                                </NavItem>
                            </>
                        )}

                    </Nav>
                    /**
                    Notifications, uses the NotificationCard as a template
                     */
                    <NavItem className="ms-auto d-flex align-items-center">
                                        <Notifications
                                            data={notifications}
                                            icon={notifLogo}
                                            imagePosition='right'
                                            width='415px'
                                            marginBottom='15px'
                                            notificationCard={NotificationCard}
                                            header={{option:{text:'Mark All As Read', onClick: () => markAllAsRead()}}}
                                        />
                                    </NavItem>
                </Collapse>
            </Navbar>
        </div>
    )
}

export default Navv
