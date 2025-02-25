import classnames from 'classnames'
import '../../css/messaging.css'
import '../../css/bootstrap.min.css'

function ConversationCard (message, conversationExchange) {
    function makeEllipses (str) {
        if (str.length > 250  && !conversationExchange)
            return str.substring(0,247) + '...';
        return str
    }

    function isDeadlineInLessThanOneDay (deadlineString) {
        return  Math.abs(Date.now() - deadlineString) < 86400000
    }

    const messageClasses = classnames({
        'p-2': true,
        'conversation-wrapper': true,
        'clickable': !conversationExchange,
        'unread': message[5] === 0,
        'deadlineApproaching': isDeadlineInLessThanOneDay(message[11])
    })
   const msg = message.message
    return (
        <div className={messageClasses}>
            <h4>
                {isDeadlineInLessThanOneDay(message[11]) ? <i className="bi-alarm"></i> : ''}
                {!conversationExchange ? msg[0] + " " + msg[1] :
                msg[2] + " - " + msg[0] + " " + msg[1]}
            </h4>
            <i className="timestamp">{msg[6]}</i>
            <p className="message_preview">{makeEllipses(msg[4])}</p>
        </div>
    )

}
export default ConversationCard