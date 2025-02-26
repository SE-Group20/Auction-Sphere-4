import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import ProductDetails from '../components/ProductDetails.js'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import axios from 'axios'
import { toast } from 'react-toastify'

jest.mock('axios')
jest.mock('react-toastify', () => ({
    toast: {
        error: jest.fn(),
    },
}))

describe('ProductDetails Component', () => {
    const mockProductData = {
        data: {
            bids: [
                ['User1', 'user1@example.com', 120],
                ['User2', 'user2@example.com', 150],
            ],
            product: [
                [
                    1,
                    'Test Product',
                    'https://example.com/image.jpg',
                    'Seller1',
                    100,
                    '2023-11-01',
                    10,
                    '2023-12-01',
                    'Sample description',
                ],
            ],
        },
    }

    beforeEach(() => {
        jest.clearAllMocks()
    })

    test('renders product details correctly when data is fetched', async () => {
        axios.post.mockResolvedValueOnce(mockProductData)

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            expect(screen.getByText('Test Product')).toBeInTheDocument()
            expect(screen.getByText('Seller: Seller1')).toBeInTheDocument()
            expect(screen.getByText('Minimum price: 100$')).toBeInTheDocument()
            expect(screen.getByText(/Sample description/i)).toBeInTheDocument()
        })
    })

    test('displays "No bids so far" when there are no bids', async () => {
        axios.post.mockResolvedValueOnce({
            data: { bids: [], product: mockProductData.data.product },
        })

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            expect(screen.getByText('No bids so far')).toBeInTheDocument()
        })
    })

    test('displays bids when available', async () => {
        axios.post.mockResolvedValueOnce(mockProductData)

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            expect(
                screen.getByText('Bidder: User1 user1@example.com')
            ).toBeInTheDocument()
            expect(screen.getByText('Bid amount: $120')).toBeInTheDocument()
            expect(
                screen.getByText('Bidder: User2 user2@example.com')
            ).toBeInTheDocument()
            expect(screen.getByText('Bid amount: $150')).toBeInTheDocument()
        })
    })

    test('displays error toast when API call fails', async () => {
        axios.post.mockRejectedValueOnce(new Error('API Error'))

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            expect(toast.error).toHaveBeenCalledWith('Something went wrong')
        })
    })

    test('shows Add Bid button when user is authenticated', async () => {
        axios.post.mockResolvedValueOnce(mockProductData)
        localStorage.setItem('auth', 'true')

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            const addBidButton = screen.getByText(/Add a Bid/i)
            expect(addBidButton).toBeInTheDocument()
        })

        localStorage.removeItem('auth')
    })

    test('shows Message Seller button when user is authenticated', async () => {
        axios.post.mockResolvedValueOnce(mockProductData)
        localStorage.setItem('auth', 'true')

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            const messageSellerButton = screen.getByText(/Message Seller/i)
            expect(messageSellerButton).toBeInTheDocument()
        })

        localStorage.removeItem('auth')
    })

    test('hide Message Seller button when user is not authenticated', async () => {
        axios.post.mockResolvedValueOnce(mockProductData)

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            const messageSellerButton = screen.getByText(/Message Seller/i)
            expect(messageSellerButton).tobeNull()
        })

        localStorage.removeItem('auth')
    })

    test('hide Add Bid button when user is not authenticated', async () => {
        axios.post.mockResolvedValueOnce(mockProductData)

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            const addBidButton = screen.getByText(/Add Bid/i)
            expect(addBidButton).tobeNull()
        })

        localStorage.removeItem('auth')
    })

    test('toggles AddBid component visibility on button click', async () => {
        axios.post.mockResolvedValueOnce(mockProductData)
        localStorage.setItem('auth', 'true')

        render(
            <MemoryRouter initialEntries={['/product/1']}>
                <Routes>
                    <Route path="/product/:id" element={<ProductDetails />} />
                </Routes>
            </MemoryRouter>
        )

        await waitFor(() => {
            const toggleButton = screen.getByText(/Add a Bid/i)
            fireEvent.click(toggleButton)
            expect(
                screen.getByPlaceholderText('Enter your bid amount here')
            ).toBeInTheDocument()
        })

        localStorage.removeItem('auth')
    })
})
