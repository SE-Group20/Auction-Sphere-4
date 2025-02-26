import { render, screen } from '@testing-library/react'
import Navv from '../components/Navv'

const tabs = [
    { text: 'Signup', location: '/signup' },
    { text: 'Login', location: '/login' },
    { text: 'Products', location: '/products' },
]
test('renders Nav bar', () => {
    render(<Navv />)
    const linkElement = screen.getByText(/Products/i)
    expect(linkElement).toBeInTheDocument()
})

test.each(tabs)('Each tab working', (tab) => {
    render(<Navv />)
    const tab_link = screen.getByText(tab.text)
    expect(tab_link).toHaveAttribute('href', tab.location)
})

test('renders navigation links when user is not authenticated', () => {
    // Mock localStorage to simulate unauthenticated user
    Object.defineProperty(window, 'localStorage', {
        value: {
            getItem: jest.fn((key) => (key === 'auth' ? 'false' : null)),
        },
        writable: true,
    })

    render(<Navv />) // Render the Navv component

    // Assert that the Login and Signup links are present
    expect(screen.getByText(/login/i)).toBeInTheDocument()
    expect(screen.getByText(/signup/i)).toBeInTheDocument()
    expect(screen.getByText(/products/i)).toBeInTheDocument()
    expect(screen.queryByText(/sell/i)).toBeNull() // Sell link should not be present
})

test('renders navigation links when user is authenticated', () => {
    // Mock localStorage to simulate authenticated user
    Object.defineProperty(window, 'localStorage', {
        value: {
            getItem: jest.fn((key) => (key === 'auth' ? 'true' : null)),
        },
        writable: true,
    })
    render(<Navv />) // Render the Navv component

    // Assert that the Sell and Logout links are present
    expect(screen.getByText(/sell/i)).toBeInTheDocument()
    expect(screen.getByText(/logout/i)).toBeInTheDocument()
    expect(screen.getByText(/messages/i)).toBeInTheDocument()
    expect(screen.getByText("Notifications")).toBeInTheDocument()
    expect(screen.queryByText(/login/i)).toBeNull()
    expect(screen.queryByText(/signup/i)).toBeNull()
})
