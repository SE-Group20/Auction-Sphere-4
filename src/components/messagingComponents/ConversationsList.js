import { useEffect, useState } from 'react'
import axios from 'axios'
import { URL } from '../../global'
import { toast } from 'react-toastify'
import { Stack } from 'react-bootstrap'
import ConversationCard from './ConversationCard'
import { Link } from 'react-router-dom'

function ConversationsList (data) {
    const [messages, setMessages] = useState([])
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get(`${URL}/messages`)
                setMessages(response.data.results)
            } catch (e) {
                toast.error(e)
            }
        }
        fetchData()
    }, [])

    function bidder_id(message) {
        return message.seller_id === message.recipient_id ? message.sender_id : message.recipient_id
    }
    return (
        <Stack gap={3}>
            {messages ? (
                messages.map((message) => (
                    <Link to={"/message/" + message.product_id + "/user/" + bidder_id(message)}>
                        <ConversationCard
                            message={message}
                            conversationExchange={false}
                            style={{backgroundColor: 'white',
                                color: 'black'}}
                        />
                    </Link>
                ))
            ) : (<i>No messages</i>)}
        </Stack>
    )
}

export default ConversationsList