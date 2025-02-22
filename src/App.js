import './App.css'
// import { Routes ,Route } from 'react-router-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import About from './components/About'
import Signup from './components/LoginSignup/Signup.js'
import Login from './components/LoginSignup/Login'
import Products from './components/Products'
import Sell from './components/Sell'
import ProductDetails from './components/ProductDetails'
import AddBid from './components/AddBid'
import Profile from './components/Profile'
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import Notifications from "react-notifications-menu"

function App() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/service-worker.js')
          .then(function(registration) {
            console.log('Service Worker registered with scope: ', registration.scope);
          })
          .catch(function(error) {
            console.error('Service Worker registration failed: ', error);
          });
      }
      

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
            </Routes>
        </>
        // </BrowserRouter>
    )
}

export default App
