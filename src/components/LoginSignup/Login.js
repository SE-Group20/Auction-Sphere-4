import React, { useState } from 'react'
import {
    Form,
    FormGroup,
    Label,
    Input,
    Navbar,
    Button,
    Card,
    CardBody,
    CardHeader,
    CardText,
} from 'reactstrap'
import axios from 'axios'
import Navv from '../Navv'
import Footer from '../Footer'
import { URL } from '../../global'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'

/**
 * This component displays the Login Page
 */
const Login = () => {
    const handleChange = (event) => {
        setFormData({ ...formData, [event.target.name]: event.target.value })
    }
    const navigate = useNavigate()
    const handleSubmit = async (event) => {
        event.preventDefault()
        console.log(formData)
        let response
        try {
            response = await axios.post(`/login`, formData, {
                headers: {
                    'Content-Type': 'application/json',
                },
                withCredentials: true,
            })
            console.log(response)
            // Set local storage
            if (response.data.message === 'Logged in successfully') {
                // alert('Login success!')
                toast.success('Login success!')
                localStorage.setItem('auth', 'true')
                localStorage.setItem('email', formData.email)
                navigate('/products')
            } else {
                toast.error('Invalid credentials!')
            }
        } catch (e) {
            toast.error('Something went wrong')
            console.log(e)
        }
    }
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    })
    return (
        <div
            style={{
                background: 'linear-gradient(30deg, #020024, #090979,#94bbe9)',
                position: 'fixed',
                top: 0,
                right: 0,
                left: 0,
                bottom: 0,
            }}
        >
            <div>
                <Navv />
                <Card
                    body
                    className="mx-auto"
                    style={{ width: '60%', margin: '10rem' }}
                >
                    <CardHeader>
                        <h3>Welcome! Login to continue</h3>
                    </CardHeader>
                    <CardBody>
                        <CardText>
                            <Form onSubmit={handleSubmit}>
                                <FormGroup>
                                    <Label for="Email">Email</Label>
                                    <Input
                                        id="Email"
                                        name="email"
                                        placeholder="The email you registered with us"
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => handleChange(e)}
                                    />
                                </FormGroup>
                                <FormGroup>
                                    <Label for="Password">Password</Label>
                                    <Input
                                        id="Password"
                                        name="password"
                                        placeholder="Your password"
                                        type="password"
                                        value={formData.password}
                                        onChange={(e) => handleChange(e)}
                                    />
                                    <br></br>
                                    <a href="/forgotPassword">
                                        <b>Forgot Password?</b>
                                    </a>
                                </FormGroup>
                                <Button color="primary">Submit</Button>
                            </Form>
                        </CardText>
                    </CardBody>
                </Card>
            </div>
        </div>
    )
}

export default Login
