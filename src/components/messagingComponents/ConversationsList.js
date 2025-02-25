import { useEffect, useState } from 'react'
import axios from 'axios'
import { URL } from '../../global'
import { toast } from 'react-toastify'
import { Stack } from 'react-bootstrap'
import ConversationCard from './ConversationCard'
import { Link } from 'react-router-dom'
import '../../css/bootstrap.min.css'


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
        return message[10] === message[8] ? message[9] : message[8]
    }
    return (
        <Stack gap={3}>
            {messages ? (
                messages.map((message) => (
                    <Link to={"/message/" + message[7] + "/user/" + bidder_id(message)}>
                        <ConversationCard
                            message={message}
                            conversationExchange={false}
                            className="conversation-wrapper"
                        />
                    </Link>
                ))
            ) : (<i>No messages</i>)}
        </Stack>
    )
}

export default ConversationsList