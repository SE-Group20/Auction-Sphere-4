import classnames from 'classnames'

function ConversationCard (message, conversationExchange) {
    function makeEllipses (str) {
        if (str.length > 250  && !conversationExchange)
            return str.substring(0,247) + '...';
        return str
    }

    const messageClasses = classnames({
        'p-2': true,
        read: message[5],
    })
   const msg = message.message
    return (
        <div className={messageClasses}>
            <h4>
                {!conversationExchange ? msg[0] + " " + msg[1] :
                msg[2] + " - " + msg[0] + " " + msg[1]}
            </h4>
            <i className="timestamp">{msg[6]}</i>
            <p className="message_preview">{makeEllipses(msg[4])}</p>
        </div>
    )

}
export default ConversationCard