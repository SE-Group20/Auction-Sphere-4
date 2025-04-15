import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import axios from 'axios'
import Watchlist from '../components/Watchlist'
import { toast } from 'react-toastify'

jest.mock('axios')
jest.mock('../components/Footer', () => () => <div data-testid="footer" />)
jest.mock('../components/Navv', () => () => <div data-testid="nav" />)
jest.mock('../components/ProductCard', () => ({ product, maxBid, name }) => (
    <div data-testid="product-card">
        {product.name} | MaxBid: {maxBid} | Bidder: {name}
    </div>
))
jest.mock('react-toastify', () => ({
    toast: {
        error: jest.fn(),
    },
}))

const mockResponse = {
    data: {
        products: [
            {
                prod_id: '1',
                name: 'Product One',
                description: 'A nice product',
            },
        ],
        maximumBids: [100],
        names: ['John Doe'],
    },
}

describe('Watchlist Component', () => {
    afterEach(() => {
        jest.clearAllMocks()
    })

    // 1. Successful API call renders ProductCard
    test('renders product cards when API returns data', async () => {
        axios.get.mockResolvedValueOnce(mockResponse)

        render(<Watchlist />)

        const card = await waitFor(() => screen.getByTestId('product-card'))
        expect(card).toHaveTextContent('Product One')
        expect(axios.get).toHaveBeenCalledWith(expect.stringContaining('/watchlist/items'))
    })

    // 2. Fallback message when no products
    test('renders fallback message when products list is empty', async () => {
        axios.get.mockResolvedValueOnce({
            data: {
                products: [],
                maximumBids: [],
                names: [],
            },
        })

        render(<Watchlist />)

        const fallback = await waitFor(() => screen.getByText(/No products found/i))
        expect(fallback).toBeInTheDocument()
    })

    // 3. API call fails → toast error shown
    test('shows toast error when API fails', async () => {
        axios.get.mockRejectedValueOnce(new Error('API down'))

        render(<Watchlist />)

        await waitFor(() => {
            expect(toast.error).toHaveBeenCalledWith('Something went wrong')
        })
    })

    // 4. Navv and Footer should always render
    test('renders navigation and footer components', async () => {
        axios.get.mockResolvedValueOnce(mockResponse)

        render(<Watchlist />)

        expect(await screen.findByTestId('nav')).toBeInTheDocument()
        expect(await screen.findByTestId('footer')).toBeInTheDocument()
    })

    // 5. Handles partial/null API response gracefully
    test('handles missing products field in API response', async () => {
        axios.get.mockResolvedValueOnce({ data: {} })

        render(<Watchlist />)

        const fallback = await waitFor(() => screen.getByText(/No products found/i))
        expect(fallback).toBeInTheDocument()
    })
})
