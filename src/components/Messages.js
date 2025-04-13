import { useEffect, useState } from 'react'
import axios from 'axios'
import { root_style, URL } from '../global'
import { toast } from 'react-toastify'
import Navv from './Navv'
import ConversationsList from './messagingComponents/ConversationsList'

const Messages = () => {
    const [data, setData] = useState(null)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.post(`${URL}/messages`)
                console.log(response.data)
                setData(response.data)
            } catch (e) {
                toast.error(e)
            }
        }
        fetchData()
    }, [])
    return (
        <>
            <div style={root_style}>
                <Navv />
                <div>
                    {data ? (
                        <>
                            <div
                                style={{
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: '10px',
                                    marginTop: '5rem',
                                    marginBottom: '20px',
                                    border: '1px solid #ddd',
                                    borderRadius: '5px',
                                    padding: '15px',
                                }}
                            >
                                <h3 style={{ color: 'white' }}>Messages</h3>
                                <ConversationsList data={data}/>
                            </div>
                        </>
                    ) : (
                        <i>No access allowed</i>
                    )}
                </div>
            </div>
        </>
    )

}

export default Messages