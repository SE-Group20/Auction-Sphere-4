import './App.css'
// import { Routes ,Route } from 'react-router-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import About from './components/About'
import Signup from './components/LoginSignup/Signup.js'
import Login from './components/LoginSignup/Login'
import Products from './components/Products'
import Messages from './components/Messages'
import Sell from './components/Sell'
import ProductDetails from './components/ProductDetails'
import AddBid from './components/AddBid'
import Profile from './components/Profile'
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import MessagesListByConversation from './components/messagingComponents/MessagesListByConversation'
import './css/bootstrap.min.css'

function App() {
    return (
        // <BrowserRouter>
        <>
            <ToastContainer />
            <Routes>
                <Route path="/" element={<About />}>
                    {/* <Route index element={<Signup />} /> */}
                </Route>
                <Route path="/signup" element={<Signup />} />
                <Route path="/login" element={<Login />} />
                <Route path="/products" element={<Products />} />
                <Route path="/sell" element={<Sell />} />
                <Route path="/details/:id" element={<ProductDetails />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/messages" element={<Messages />} />
                <Route path="/message/:product_id/user/:bidder_id" element={<MessagesListByConversation />} />
            </Routes>
        </>
        // </BrowserRouter>
    )
}

export default App
