import { useEffect, useState } from 'react'
import axios from 'axios'
import { URL } from '../../global'
import { toast } from 'react-toastify'
import { Stack } from 'react-bootstrap'
import ConversationCard from './ConversationCard'

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
    return (
        <Stack gap={3}>
            {messages ? (
                messages.map((message) => (
                    <ConversationCard message={message}/>
                ))
            ) : (<i>No messages</i>)}
        </Stack>
    )
}

export default ConversationsList