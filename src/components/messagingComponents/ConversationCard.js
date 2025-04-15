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
        'unread': message.read === 0,
        'deadlineApproaching': isDeadlineInLessThanOneDay(message.deadline_date)
    })
   const msg = message.message
   console.log("msg", msg)
    return (
        <div className={messageClasses}>
            <h4>
                {isDeadlineInLessThanOneDay(msg.deadline_date) ? <i className="bi-alarm"></i> : ''}
                {!conversationExchange ? msg.first_name + " " + msg.last_name :
                msg.product_name + " - " + msg.first_name + " " + msg.last_name}
            </h4>
            <i className="timestamp">{msg.time_sent}</i>
            <p className="message_preview">{makeEllipses(msg.message)}</p>
        </div>
    )

}
export default ConversationCard