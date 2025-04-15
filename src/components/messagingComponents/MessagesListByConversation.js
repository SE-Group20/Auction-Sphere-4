import { useEffect, useState } from 'react'
import axios from 'axios'
import { root_style, URL } from '../../global'
import { toast } from 'react-toastify'
import Navv from '../Navv'
import ConversationsList from './ConversationsList'
import { useParams } from 'react-router-dom'
import { Stack } from 'react-bootstrap'
import ConversationCard from './ConversationCard'

function MessagesListByConversation () {
    const { product_id, bidder_id } = useParams()
    const [messages, setMessages] = useState([])
    const [newMessage, setNewMessage] = useState("")

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

    const handleSubmit = async () => {
        try {
            const lastMessage = messages[0]
            console.log('lastMessage', lastMessage)
            console.log('newMessage', newMessage)
            await axios.post(`${URL}/message`, {
                product_id: lastMessage[8],
                recipient_id: lastMessage[7],
                message: newMessage
            })
        } catch (e) {
            console.log(e)
            toast.error('Error submitting message')

        }
    }

    return (
        <>
            <div
                style={root_style}
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
                                    {messages
                                        ? messages.map((message) => (
                                              <ConversationCard
                                                  message={message}
                                                  conversationExchange={true}
                                                  key = {message[7]}
                                              />
                                          ))
                                        : 'No messages found'}
                                </Stack>

                                <div className="form">
                                    <textarea
                                        className="form-control"
                                        placeholder="Your Message here"
                                        id="newMessage"
                                        onChange={(e) => setNewMessage(e.target.value)}
                                    ></textarea>
                                    <label for="newMessage">New Message</label>
                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        onClick={handleSubmit}
                                    >
                                        Submit Message
                                    </button>
                                </div>
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