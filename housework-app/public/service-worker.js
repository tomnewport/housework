/* eslint-disable no-restricted-globals */

const appBaseUrl = process.env.PUBLIC_URL || "http://localhost:3000";

self.addEventListener("install", (event) => {});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("push", function (event) {
  const data = event.data.json();
  const options = {
    body: data.body,
    data: data.id,
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

self.addEventListener("notificationclick", function (event) {
  event.notification.close(); // Close the notification
  const notificationId = event.notification.data;

  // URL to navigate to
  const urlToOpen = new URL(`/notification/${notificationId}`, appBaseUrl).href;

  const promiseChain = self.clients
    .matchAll({
      type: "window",
      includeUncontrolled: true,
    })
    .then((windowClients) => {
      const found = [...windowClients]
        .sort((a) => (a.visibilityState === "visible" ? -1 : 1))
        .find(({ url }) => url.startsWith(appBaseUrl));

      if (found) {
        return found.focus().then((client) => {
          return client.postMessage({
            action: "goto",
            url: `/notification/${notificationId}`,
          });
        });
      } else {
        return self.clients.openWindow(urlToOpen);
      }
    })
    .catch((err) => console.error(err));

  event.waitUntil(promiseChain);
});
