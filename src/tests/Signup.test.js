import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Signup from '../components/LoginSignup/Signup.js'
import { BrowserRouter as Router } from 'react-router-dom'
const fields = [
    { field_label: 'First Name', node_name: 'firstName' },
    { field_label: 'Last Name', node_name: 'lastName' },
    { field_label: 'Contact Number', node_name: 'contact' },
    { field_label: 'Email', node_name: 'email' },
    { field_label: 'Password', node_name: 'password' },
    { field_label: 'Confirm Password', node_name: 'confirmPassword' },
]
test.each(fields)('Rendering the signup form', (field) => {
    render(
        <Router>
            <Signup />
        </Router>
    )
    const label = screen.getByText(field.field_label)
    expect(label).toBeInTheDocument()
})

test.each(fields)('Fields have labels', (field) => {
    render(
        <Router>
            <Signup />
        </Router>
    )
    const inputNode = screen.getByLabelText(field.field_label)
    expect(inputNode.getAttribute('name')).toBe(field.node_name)
})

test('cannot submit form when passwords do not match', async() => {
    render(<Router><Signup/></Router>)
    fireEvent.change(screen.getByLabelText('First Name'), {target: {value: 'Jane'}})
    fireEvent.change(screen.getByLabelText('Last Name'), {target: {value: 'Doe'}})
    fireEvent.change(screen.getByLabelText('Contact Number'), {target: {value: '1234567890'}})
    fireEvent.change(screen.getByLabelText('Email'), {target: {value: 'test@email.com'}})
    fireEvent.change(screen.getByLabelText('Password'), {target: {value: 'password'}})
    fireEvent.change(screen.getByLabelText('Confirm Password'), {target: {value: 'password2'}})

    fireEvent.click(screen.getByText("Submit"))

    await waitFor(() => expect(screen.getByText("Passwords do not match").toBeInTheDocument()))
})

test('check that all fields are filled in on sign up page', async() => {
    render(<Router><Signup/></Router>)
    fireEvent.change(screen.getByLabelText('First Name'), {target: {value: 'Jane'}})
    fireEvent.change(screen.getByLabelText('Contact Number'), {target: {value: '1234567890'}})
    fireEvent.change(screen.getByLabelText('Email'), {target: {value: 'test@email.com'}})
    fireEvent.change(screen.getByLabelText('Password'), {target: {value: 'password'}})
    fireEvent.change(screen.getByLabelText('Confirm Password'), {target: {value: 'password'}})

    fireEvent.click(screen.getByText("Submit"))

    await waitFor(() => screen.getByText("is required").toBeInTheDocument())
})

// "transform": {
//   "^.+\\.[t|j]sx?$": "babel-jest"
// },
