import React, { useEffect, useState } from 'react'
import Footer from './Footer'
import Navv from './Navv'
import ProductCard from './ProductCard'
import { URL } from '../global'
import axios from 'axios'
import { CardGroup, Row } from 'reactstrap'
import { toast } from 'react-toastify'

const Watchlist = () => {
     //CHANGE CODE TO WATCHLIST PRODUCTS ONLY 
    const [apiData, setApiData] = useState([])

    const getProducts = async () => {
        try {
            let data = await axios.get(`${URL}/getLatestProducts`)
            console.log(data.data)
            setApiData(data.data)
        } catch (error) {
            toast.error('Something went wrong')
            console.log(error)
        }
    }
    useEffect(() => {
        getProducts()
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
                }}
            >
                <Navv />
                <Row style={{ margin: '5rem' }}>
                    {apiData && apiData.products ? (
                        apiData.products.map((product, index) => (
                            <ProductCard
                                key={index}
                                product={product}
                                maxBid={apiData.maximumBids[index]}
                                name={apiData.names[index]}
                            />
                        ))
                    ) : (
                        <div>No products found</div>
                    )}
                </Row>
                <Footer />
            </div>
        </>
    )

}

export default Watchlist