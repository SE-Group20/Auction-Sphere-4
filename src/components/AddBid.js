import React, { useState } from 'react'
import { Form, FormGroup, Label, Input, Navbar, Button } from 'reactstrap'
import axios from 'axios'
import { URL } from '../global'
import PropTypes from 'prop-types'
import { toast } from 'react-toastify'

/**
 * This component lets you bid on a product you like.
 */

const AddBid = ({ productId, sellerEmail }) => {
    const [amount, setAmount] = useState(0)
    const handleChange = (event) => {
        setAmount(event.target.value)
    }
    const handleSubmit = async (event) => {
        event.preventDefault()
        console.log(amount)
        let response
        try {
            if (typeof window !== 'undefined') {
                if (localStorage.getItem('email') === sellerEmail) {
                    toast.error('Cannot bid on your own product!')
                } else {
                    const response = await axios.post(`${URL}/bid/create`, {
                        bidAmount: amount,
                        prodId: productId,
                        email: localStorage.getItem('email'),
                    });

                    if (response.status === 200) {
                        toast.success(response.data.message)
                        const owner = await axios.post(`${URL}/getOwner`, {
                            productID: productId
                        })
                        console.log(owner)
                        // Send a notification after a successful bid
                        await axios.post(`${URL}/notifications`, {
                            user_id: owner.data.result[0][0],  // Assuming email is the user ID
                            message: `Your bid of $${amount} has been placed on : ${productId}.`,
                            detail_page: `/product/${productId}` // A link to the product details page
                        });
                        console.log({URL})
                        toast.info('Notification sent successfully!');
                        window.location.reload(false);
                    }
                }
            }
        } catch (e) {
            console.log(e)
            toast.error('Error placing bid')
        }
    }
    return (
        <div style={{ marginTop: '1rem' }}>
            Add a bid for product {productId}
            <Form onSubmit={handleSubmit}>
                <FormGroup>
                    <Label for="amount">Amount:</Label>
                    <Input
                        className="mx-auto"
                        style={{ width: '50%' }}
                        id="amount"
                        name="amount"
                        placeholder="Enter your bid amount here"
                        type="amount"
                        value={amount}
                        onChange={(e) => handleChange(e)}
                    />
                </FormGroup>
                <Button color="primary">Submit</Button>
            </Form>
        </div>
    )
}
AddBid.propTypes = {
    productId: PropTypes.number.isRequired,
}

export default AddBid
