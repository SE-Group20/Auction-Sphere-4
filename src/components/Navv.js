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
import logo from '../assets/NavLogo.png'
import cabinet from '../assets/cabinet.jpg'

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
    
    const data = 
        [
        {
          message : 'Someone just bid!',
          detailPage : '/products', 
          receivedTime:'12h ago'
        }
     ]
    
    const fetchNotifications = async () => {
        try {
            const user_id = 1;
            const response = await axios.get(`/notifications/${user_id}`);
            setNotifications(response.data.notifications);
        } catch (error) {
            console.error("Error fetching notifications:", error);
        }
    };

    // Fetch Notifications on Mount & Every 30s
    useEffect(() => {
        fetchNotifications(); // Initial fetch

        const interval = setInterval(() => {
            fetchNotifications(); // Poll every 30s
        }, 10000);

        return () => clearInterval(interval); // Cleanup on unmount
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
                    <Nav className="justify-content-end" navbar>
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
                                        style={{ color: 'white' }}
                                        href="/"
                                        onClick={handleLogout}
                                    >
                                        Logout
                                    </NavLink>
                                </NavItem>
                                <Nav></Nav>
                                <Nav className="ms-auto">
                                    <NavLink
                                        style={{ color: 'white' }}
                                        href="/profile"
                                    >
                                        Profile
                                    </NavLink>
                                </Nav>
                                <Nav className="ms-auto">
                                <Notifications 
                                data={data} />
                                </Nav>
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
                </Collapse>
            </Navbar>
        </div>
    )
}

export default Navv
