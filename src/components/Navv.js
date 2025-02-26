import React, { useState } from 'react'
import { toast } from 'react-toastify'
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
import logo from '../assets/NavLogo.png'

/**
 * This component is the Navigation bar of our application.
 */

function Navv(args) {
    const [isOpen, setIsOpen] = useState(true)

    const toggle = () => setIsOpen(!isOpen)
    const handleLogout = () => {
        localStorage.clear()
        window.location.reload()
        toast.info('Logged out')
    }

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
                                <Nav></Nav>
                                <Nav className="ms-auto">
                                    <NavLink
                                        style={{ color: 'white' }}
                                        href="/profile"
                                    >
                                        Profile
                                    </NavLink>
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
