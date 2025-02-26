self.addEventListener('push', function(event) {
    const options = {
      body: event.data.text(),  // The payload of the push message
      icon: '/icons/notification-icon.png',  // Icon for the notification
      badge: '/icons/notification-badge.png',  // Badge for the notification
    };
  
    event.waitUntil(
      self.registration.showNotification('New Notification', options)
    );
  });
  
  self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
      clients.openWindow('https://your-website.com')  // Open the website when the notification is clicked
    );
  });
  