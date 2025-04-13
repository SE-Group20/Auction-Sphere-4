import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Button, Card, CardImg, CardTitle, CardText } from 'reactstrap'
import axios from 'axios'

import AddBid from './AddBid'
import Navv from './Navv'
import { isLoggedIn, root_style, URL } from '../global'
import { toast } from 'react-toastify'
import CountdownTimer from './Countdown'
/**
 * This component is the details page of a single product.
 */

function calcDate(inputDate) {
    return new Date(inputDate)
}
const ProductDetails = () => {
    let { id } = useParams()
    const [showAddBid, setShowAddBid] = useState(false)
    const [showButton, setShowButton] = useState(false)
    const [bids, setBids] = useState([])
    const [product, setProduct] = useState(null)
    const getProductDetails = async () => {
        try {
            let data = await axios.post(`${URL}/product/getDetails`, {
                productID: id,
            })
            console.log(data)
            setBids(data.data.bids)
            setProduct(data.data.product)
        } catch (error) {
            toast.error('Something went wrong')
        }
    }
    useEffect(() => {
        getProductDetails()
        if (typeof window !== 'undefined') {
            if (isLoggedIn()) {
                setShowButton(true)
            }
        }
    }, [])

    const sendMessage = async () => {
        try {
            let response = await axios.post(`${URL}/message`, {
                product_id: id,
                recipient_id: product.name,
                message: "hi I am interested in your product"
            })
            console.log(response)
            toast.success("Message sent successfully. Check message inbox")
        } catch (error) {
            toast.error(error)
        }
    }

    return (
        <>
            <div
                style={root_style}
            >
                <Navv />
                <Card
                    className="mx-auto"
                    color="light"
                    outline
                    style={{
                        width: '45rem',
                        margin: '5rem',
                        textAlign: 'center',
                    }}
                >
                    {product && (
                        <div>
                            <CardTitle tag="h3" style={{ textAlign: 'center' }}>
                                {product[1]}{' '}
                            </CardTitle>
                            <CardTitle style={{ textAlign: 'right' }}>
                                <CountdownTimer
                                    targetDate={calcDate(product.deadline_date)}
                                />
                            </CardTitle>
                            <hr />
                            <CardImg
                                src={product.prod_id}
                                className="mx-auto"
                                style={{ width: '50%' }}
                            />
                            <CardText>
                                <p>Seller:&nbsp;&nbsp;{product.seller_email} </p>
                                <p>
                                    Minimum price:
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                    {product.initial_price}${' '}
                                </p>
                                <p>
                                    Date posted: &nbsp;&nbsp;&nbsp;{product.date}{' '}
                                </p>
                                <p>
                                    Bidding window closes on: &nbsp;&nbsp;&nbsp;
                                    {product.deadline_date}{' '}
                                </p>
                                <p>
                                    Minimum price increment to beat a bid:
                                    &nbsp;&nbsp;&nbsp;
                                    {product.increment}${' '}
                                </p>
                                <p>
                                    Product Description: &nbsp;&nbsp;
                                    {product.description}{' '}
                                </p>
                                {bids.length > 0 ? (
                                    <>
                                        <h5>Current Highest bids:</h5>
                                        {bids.map((bid, index) => (
                                            <div key={index}>
                                                <p>
                                                    Bidder:{' '}
                                                    {bid[0] + ' ' + bid[1]}
                                                </p>
                                                <p>Bid amount: ${bid[2]}</p>
                                            </div>
                                        ))}
                                    </>
                                ) : (
                                    <h5>No bids so far</h5>
                                )}
                                {showButton && (
                                    <>
                                        <Button
                                            color="info"
                                            onClick={() =>
                                                setShowAddBid(!showAddBid)
                                            }
                                        >
                                            {showAddBid ? (
                                                <span>-</span>
                                            ) : (
                                                <span>+</span>
                                            )}{' '}
                                            Add a Bid
                                        </Button>
                                        {showAddBid && (
                                            <AddBid
                                                productId={id}
                                                sellerEmail={product.seller_email}
                                            />
                                        )}
                                        <Button
                                            color="info"
                                            onClick={() => sendMessage()}
                                        >
                                            Message Seller
                                        </Button>
                                    </>
                                )}
                            </CardText>
                        </div>
                    )}
                </Card>
            </div>
        </>
    )
}

export default ProductDetails
