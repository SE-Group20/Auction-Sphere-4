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
                    const prevBidder = await axios.get(`${URL}/bid/get`, {
                        params: {productID: productId}
                    })


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
                        const prodName = await axios.get(`${URL}/getName`, {
                            params: {productID: productId}
                        })
                        console.log(owner)

                        // Get all users who have this product in watchlist
                        const watchers = await axios.get(`${URL}/watchlist/users`, {
                            params: { productId: productId }
                        })

                        // Send a notification after a successful bid
                        await axios.post(`${URL}/notifications`, {
                            user_id: owner.data.result[0][0], 
                            
                            message: `A bid of $${amount} has been placed on : ${prodName.data.result}.`,
                            detail_page: `/details/${productId}` // A link to the product details page
                        });

                        // Send a notification after a successful bid
                        if (prevBidder && prevBidder.data.result.length > 0) {
                            const email = prevBidder.data.result[0]
                            if (email !== localStorage.getItem('email')) {
                                await axios.post(`${URL}/notifications`, {
                                    user_id: prevBidder.data.result[0][0], 
                                    
                                    message: `A bid of $${amount} has been placed on : ${prodName.data.result}.`,
                                    detail_page: `/details/${productId}` // A link to the product details page
                                });
                            }  
                        }

                        // Notify all watchers
                        if (watchers.data.users && watchers.data.users.length > 0) {

                            for (const watcher of watchers.data.users) {
                                await axios.post(`${URL}/notifications`, {
                                    user_id: watcher.user_id,
                                    message: `A bid of $${amount} has been placed on : ${prodName.data.result}.`,
                                    detail_page: `/details/${productId}` // A link to the product details page
                                })
                            }
                        }
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
