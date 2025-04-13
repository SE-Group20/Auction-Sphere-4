import React from 'react'
import Navv from './Navv'
import logo from '../assets/Logo.png'
import '../css/about.css'
import myGif from '../assets/auction.gif'
import cabinet from '../assets/cabinet.jpg'
import couch from '../assets/couch.jpeg'
import hairdryer from '../assets/Hair_dryer.jpeg'
import lamp from '../assets/lamp.jpg'
import painting from '../assets/Starry-Night.webp'
import treadmill from '../assets/treadmill.webp'
import sunglass from '../assets/sungalss.jpeg'
import ProductView from './ProductView'
import '../css/gallery.css'
import logo2 from '../assets/logo_new2.png'
import { root_style } from '../global'
/**
 * This component displays information about our project.
 */

const About = () => {
    return (
        <>
            <div
                style={root_style}
            >
                <Navv />
                <div
                    style={{
                        textAlign: 'center',
                        color: 'white',
                        margin: '4rem',
                    }}
                >
                    <h1 style={{ padding: 10 }}>Welcome to Auction-Sphere!</h1>

                    <p>
                        One-stop shop for your favourite items at desired
                        prices!
                        <br></br>
                        Bid for exciting items and grab your favourite!
                    </p>
                </div>
                <div
                    className="scroll-container"
                    style={{ position: 'absolute', left: 5, top: '13rem' }}
                >
                    <a href="/Products">
                        <img
                            src={couch}
                            alt="Cinque Terre"
                            width="250"
                            height="250"
                        ></img>
                        <img
                            src={hairdryer}
                            alt="Forest"
                            width="250"
                            height="250"
                        ></img>
                        <img
                            src={painting}
                            alt="Northern Lights"
                            width="250"
                            height="250"
                        ></img>
                        <img
                            src={sunglass}
                            alt="Mountains"
                            width="250"
                            height="250"
                        ></img>
                        <img
                            src={cabinet}
                            alt="Mountains"
                            width="250"
                            height="250"
                        ></img>
                        <img
                            src={lamp}
                            alt="Mountains"
                            width="250"
                            height="250"
                        ></img>
                        <img
                            src={treadmill}
                            alt="Mountains"
                            width="250"
                            height="250"
                        ></img>
                    </a>
                </div>
                <div
                    className="about-us"
                    style={{
                        textAlign: 'left',
                        top: 500,
                        width: 1150,
                        left: 10,
                        opacity: 0.8,
                    }}
                >
                    {' '}
                    <h3>About Us</h3>
                    <p>
                        Auction Sphere is an auctioning system where people can
                        bid on exciting items and also put items up for sale.
                        Every item has a bidding window, and the item goes to
                        the highest bidder by the end of that window. It is
                        agreat place to look for exciting items at your desired
                        price!
                    </p>
                    <h3>How does it Work?</h3>
                    <div>
                        <ol>
                            <li>Register your Profile on our webiste</li>
                            <li>
                                Add a product and its details, for others to bid
                                on!
                            </li>
                            <li>
                                Place bids on products to grab your favourites!
                            </li>
                            <li>
                                track the progress of items in your Personalized
                                dashboard
                            </li>
                        </ol>
                        To learn about the exiting products on our webiste,
                        please check out our
                        <a href="/products" style={{ color: 'white' }}>
                            <b>Products!</b>
                        </a>
                    </div>
                </div>
                <img
                    src={logo2}
                    style={{
                        height: 160,
                        width: 300,
                        position: 'absolute',
                        right: 7,
                        bottom: 7,
                        borderRadius: 5,
                    }}
                />
            </div>
        </>
    )
}

export default About
