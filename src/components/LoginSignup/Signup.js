import React, { useState } from 'react'
import {
    Form,
    FormGroup,
    Label,
    Input,
    Button,
    Card,
    CardBody,
    CardText,
    CardTitle,
    CardHeader,
} from 'reactstrap'
import { useNavigate } from 'react-router-dom'
import Navv from '../Navv'
import Footer from '../Footer'
import axios from 'axios'
import { isLoggedIn, root_style, URL } from '../../global'
import { toast } from 'react-toastify'

/**
 * This component displays the Signup page of our application.
 */

const Signup = () => {
    const navigate = useNavigate()
    const handleChange = (event) => {
        setFormData({ ...formData, [event.target.name]: event.target.value })
        setErrors((prevErrors) => ({ ...prevErrors, [event.target.name]: '' }));
    }

    const formatPhoneNumber = (value) => {
        const numbers = value.replace(/\D/g, '');

        if (numbers.length <= 3) return numbers;
        if (numbers.length <= 6) return `(${numbers.slice(0, 3)}) ${numbers.slice(3)}`;
        return `(${numbers.slice(0, 3)}) ${numbers.slice(3, 6)}-${numbers.slice(6, 10)}`;
    };

    const handleChangePhone = (event) => {
        const formattedNumber = formatPhoneNumber(event.target.value)
        setFormData({ ...formData, [event.target.name]: formattedNumber })
        setErrors((prevErrors) => ({ ...prevErrors, [event.target.name]: '' }));
    }

    const formatFieldName = (field) => {
        return field
            .replace(/([A-Z])/g, ' $1')
            .trim()
            .replace(/\b\w/g, (char) => char.toUpperCase());
    };

    const handleSubmit = async (event) => {
        event.preventDefault()
        let newErrors = {};
        Object.keys(formData).forEach((key) => {
            if (typeof formData[key] === "string" && formData[key].trim() === "") {
              errors[key] = "This field is required";
            }
          });          
        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            toast.error('Fill out all fields before submitting');
            return;
        }
        if (formData.password !== formData.confirmPassword)
            toast.error('Passwords do not match')
        else if (formData.password === '')
            toast.error('Must have a password')
        else {
            console.log(formData)
            try {
                const strippedNumber = formData.contact.replace(/\D/g, '');
                const updatedFormData = { ...formData, contact: strippedNumber };

                const response = await axios.post(`${URL}/signup`, updatedFormData);
                console.log(response)
                navigate('/login')
                // alert("Form submitted successfully I think");
            } catch (e) {
                const errorMessage = e.response.data.message;
                toast.error(errorMessage);
                console.log(e)
            }
        }
        
    }
    const [formData, setFormData] = useState({
        firstName: '',
        lastName: '',
        contact: '',
        email: '',
        // address: "",
        password: '',
        confirmPassword: '',
        emailOptIn: false,
    })
    const [errors, setErrors] = useState({});
    return (
            <div style={root_style}>
                <Navv />
                {isLoggedIn() ? (
                    <></>
                ) : (
                    <>
                        <Card
                            body
                            className="mx-auto"
                            style={{ width: '60%', margin: '6rem' }}
                        >
                            <CardHeader>
                                <h3>Sign up and bid away!</h3>
                            </CardHeader>
                            <CardBody>
                                <CardText>
                                    <Form onSubmit={handleSubmit}>
                                        <FormGroup>
                                            <Label for="FirstName">
                                                First Name
                                            </Label>
                                            <Input
                                                id="FirstName"
                                                name="firstName"
                                                placeholder="Your first name"
                                                type="text"
                                                value={formData.firstName}
                                                onChange={(e) =>
                                                    handleChange(e)
                                                }
                                                style={{
                                                    borderColor: errors.firstName ? 'red' : '',
                                                    borderWidth: errors.firstName ? '2px' : '',
                                                }}
                                            />
                                            {errors.firstName && <small style={{ color: 'red' }}>{errors.firstName}</small>}
                                        </FormGroup>
                                        <FormGroup>
                                            <Label for="LastName">
                                                Last Name
                                            </Label>
                                            <Input
                                                id="LastName"
                                                name="lastName"
                                                placeholder="Family name"
                                                type="text"
                                                value={formData.lastName}
                                                onChange={(e) =>
                                                    handleChange(e)
                                                }
                                                style={{
                                                    borderColor: errors.firstName ? 'red' : '',
                                                    borderWidth: errors.firstName ? '2px' : '',
                                                }}
                                            />
                                            {errors.lastName && <small style={{ color: 'red' }}>{errors.lastName}</small>}
                                        </FormGroup>
                                        <FormGroup>
                                            <Label for="Contact">
                                                Contact Number
                                            </Label>
                                            <Input
                                                id="Contact"
                                                name="contact"
                                                placeholder="(123) 456-7890"
                                                type="text"
                                                value={formData.contact}
                                                onChange={(e) =>
                                                    handleChangePhone(e)
                                                }
                                                style={{
                                                    borderColor: errors.contact ? 'red' : '',
                                                    borderWidth: errors.contact ? '2px' : '',
                                                }}
                                            />
                                            {errors.contact && <small style={{ color: 'red' }}>{errors.contact}</small>}
                                        </FormGroup>
                                        <FormGroup>
                                            <Label for="Email">Email</Label>
                                            <Input
                                                id="Email"
                                                name="email"
                                                placeholder="abc@gmail.com"
                                                type="email"
                                                value={formData.email}
                                                onChange={(e) =>
                                                    handleChange(e)
                                                }
                                                style={{
                                                    borderColor: errors.email ? 'red' : '',
                                                    borderWidth: errors.email ? '2px' : '',
                                                }}
                                            />
                                            {errors.email && <small style={{ color: 'red' }}>{errors.email}</small>}
                                        </FormGroup>
                                        {/* <FormGroup>
          <Label for="Address">Address</Label>
          <Input
            id="Address"
            name="address"
            placeholder="We promise to not come over, atleast not unannounced :)"
            type="textarea"
            value={formData.address}
            onChange={(e) => handleChange(e)}
          />
        </FormGroup> */}
                                        <FormGroup>
                                            <Label for="Password">
                                                Password
                                            </Label>
                                            <Input
                                                id="Password"
                                                name="password"
                                                placeholder="Password"
                                                type="password"
                                                value={formData.password}
                                                onChange={(e) =>
                                                    handleChange(e)
                                                }
                                                style={{
                                                    borderColor: errors.password ? 'red' : '',
                                                    borderWidth: errors.password ? '2px' : '',
                                                }}
                                            />
                                            {errors.password && <small style={{ color: 'red' }}>{errors.password}</small>}
                                        </FormGroup>
                                        <FormGroup>
                                            <Label for="ConfirmPassword">
                                                Confirm Password
                                            </Label>
                                            <Input
                                                id="ConfirmPassword"
                                                name="confirmPassword"
                                                placeholder="Confirm Password"
                                                type="password"
                                                value={formData.confirmPassword}
                                                onChange={(e) =>
                                                    handleChange(e)
                                                }
                                                style={{
                                                    borderColor: errors.confirmPassword ? 'red' : '',
                                                    borderWidth: errors.confirmPassword ? '2px' : '',
                                                }}
                                            />
                                            {errors.confirmPassword && <small style={{ color: 'red' }}>{errors.confirmPassword}</small>}
                                        </FormGroup>

                                        <FormGroup check>
                                            <Input
                                                type="checkbox"
                                                id="emailOptIn"
                                                name="emailOptIn"
                                                checked={formData.emailOptIn || false}
                                                onChange={(e) => setFormData({ ...formData, emailOptIn: e.target.checked })}
                                            />
                                            <Label check htmlFor="emailOptIn">
                                                Receive email notifications for new bids
                                            </Label>
                                            </FormGroup>

                                        <Button color="primary">Submit</Button>
                                    </Form>
                                </CardText>
                            </CardBody>
                        </Card>

                        <br />
                    </>
                )}
                <Footer style={{ margin: '1rem' }}></Footer>
            </div>
    )
}

export default Signup
