// configurable base url. blank is best for cookie compatability
const URL = ''

const root_style={
    background:
        'linear-gradient(30deg, #020024, #090979,#94bbe9)',
    backgroundAttachment: 'scroll',
    position: 'absolute',
    margin: '0',
    width: '100%',
    top: 0,
    left: 0,
}

// check if user is logged in
const isLoggedIn = () => {
    return localStorage.getItem('auth') === 'true'
}

export { URL, root_style, isLoggedIn }

