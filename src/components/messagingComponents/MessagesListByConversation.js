import { useEffect, useState } from 'react'
import axios from 'axios'
import { URL } from '../../global'
import { toast } from 'react-toastify'
import Navv from '../Navv'
import ConversationsList from './ConversationsList'
import { useParams } from 'react-router-dom'
import { Stack } from 'react-bootstrap'
import ConversationCard from './ConversationCard'

function MessagesListByConversation () {
    const { product_id, bidder_id } = useParams()
    const [messages, setMessages] = useState([])
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`${URL}/message/product/` + product_id + `/bidder/` + bidder_id)
                setMessages(response.data)
            } catch (e) {
                toast.error(e)
            }
        }
        fetchData()
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
                <div>
                    {messages ? (
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
                                <Stack gap={3}>
                                    {messages ? messages.map((message) => (
                                        <ConversationCard
                                            message={message}
                                            conversationExchange={true}
                                        />
                                    )) : 'No messages found'}
                                </Stack>
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

export default MessagesListByConversation