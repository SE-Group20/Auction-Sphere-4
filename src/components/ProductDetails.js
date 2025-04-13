import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Button, Card, CardImg, CardTitle, CardText } from 'reactstrap'
import axios from 'axios'

import AddBid from './AddBid'
import Navv from './Navv'
import { URL } from '../global'
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
    const [isInWatchlist, setIsInWatchlist] = useState(false);
    const [image, setImage] = useState(null)

    const getProductDetails = async () => {
        try {
            let data = await axios.post(`${URL}/product/getDetails`, {
                productID: id,
            })
            console.log(data)
            setBids(data.data.bids)
            setProduct(data.data.product[0])
        } catch (error) {
            toast.error('Something went wrong')
        }
    }

    useEffect(() => {
        getProductDetails()
        if (typeof window !== 'undefined') {
            if (localStorage.getItem('auth') === 'true') {
                setShowButton(true);
                checkWatchlistStatus();
            }
        }
    }, [])

    const toggleWatchlist = async () => {
        try {
            if (isInWatchlist) {

                let data = await axios.post(`${URL}/watchlist/remove`, {
                    productID: id,
                })
                console.log(data)
                // await axios.post(`${URL}/watchlist/remove`, {
                //     product_id: id,
                //     user_id: localStorage.getItem('userID') // Assuming you store userID in localStorage
                // });
                toast.success("Removed from watchlist");
            } else {
                let data = await axios.post(`${URL}/watchlist/add`, {
                    productID: id,
                })
                console.log(data)
                // await axios.post(`${URL}/watchlist/add`, {
                //     product_id: id,
                //     user_id: localStorage.getItem('userID')
                // });
                toast.success("Added to watchlist");
            }
            setIsInWatchlist(!isInWatchlist);
        } catch (error) {
            toast.error("Failed to update watchlist");
        }
    };

    const sendMessage = async () => {
        try {
            let response = await axios.post(`${URL}/message`, {
                product_id: id,
                recipient_id: product[0],
                message: "hi I am interested in your product"
            })
            console.log(response)
            toast.success("Message sent successfully. Check message inbox")
        } catch (error) {
            toast.error(error)
        }
    }


    const checkWatchlistStatus = async () => {
        try {
            const response = await axios.post(`${URL}/watchlist/check`, {
                productID: id,
                userID: localStorage.getItem('userID')
            });
            setIsInWatchlist(response.data.isInWatchlist);
        } catch (error) {
            console.error("Error checking watchlist:", error);
        }
    };

    const fetchImage = async () => {
        try {
            const response = await axios.post(`${URL}/product/getImage`, {
                productID: product[0],
            })
            console.log(response)
            setImage(response.data.result[0])
        } catch (e) {
            toast.error(e)
        }
    }

    useEffect(() => {
        fetchImage()
    }, [])



    return (
        <>
            <div
                style={{
                    background:
                        'linear-gradient(30deg, #020024, #090979,#94bbe9)',
                    backgroundAttachment: 'scroll',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                }}
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
                                    targetDate={calcDate(product[7])}
                                />
                            </CardTitle>
                            <hr />
                            <CardImg
                                src={image}
                                className="mx-auto"
                                style={{ width: '50%' }}
                            />
                            <CardText>
                                <p>Seller:&nbsp;&nbsp;{product[2]} </p>
                                <p>
                                    Minimum price:
                                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                    {product[3]}${' '}
                                </p>
                                <p>
                                    Date posted: &nbsp;&nbsp;&nbsp;{product[4]}{' '}
                                </p>
                                <p>
                                    Bidding window closes on: &nbsp;&nbsp;&nbsp;
                                    {product[6]}{' '}
                                </p>
                                <p>
                                    Minimum price increment to beat a bid:
                                    &nbsp;&nbsp;&nbsp;
                                    {product[5]}${' '}
                                </p>
                                <p>
                                    Product Description: &nbsp;&nbsp;
                                    {product[7]}{' '}
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
                                            style={{ margin: '5px' }}
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
                                                sellerEmail={product[3]}
                                            />
                                        )}
                                        <Button
                                            color="info"
                                            onClick={() => sendMessage()}
                                            style={{ margin: '5px' }}
                                        >
                                            Message Seller
                                        </Button>
                                        <Button 
                                            color="info"
                                            onClick={() => toggleWatchlist()}
                                            style={{ margin: '5px' }}
                                        >
                                            {isInWatchlist ? "Remove from Watchlist" : "Add to Watchlist"}
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
