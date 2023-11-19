import { useEffect, useMemo, useState } from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";
import Site from "./components/Site";
import {
  useMarkNotificationAsReadMutation,
  useSubscribeMutation,
} from "./services/housework/notifications";
import UAParser from "ua-parser-js";
import { v4 as uuidv4 } from "uuid";
import useNotificationPermission from "./components/notification/useNotificationPermission";
import { debounce } from "@mui/material";
import { useDispatch } from "react-redux";
import apiService from "./services/housework";
import AuthWall from "./components/auth/AuthWall";
import { useGetSelfQuery } from "./services/housework/auth";

function NotificationRedirect() {
  const navigate = useNavigate();
  const { notificationId = "0" } = useParams();
  const [markRead] = useMarkNotificationAsReadMutation();
  const [isError, setIsError] = useState<boolean>(false);

  useEffect(() => {
    markRead(parseInt(notificationId))
      .unwrap()
      .then((url) => navigate(url))
      .catch(() => setIsError(true));
  }, [markRead, navigate, notificationId]);

  if (!isError) return null;
  return (
    <p>
      Error - notification no longer exists!{" "}
      <button onClick={() => navigate("/")}>OK</button>
    </p>
  );
}

function createClientId() {
  const newUUID = uuidv4();
  const ua = new UAParser();
  const id = `${ua.getBrowser()?.name} on ${ua.getOS()?.name}|${newUUID}`;
  window.localStorage.setItem("housework.x-client-id", id);
  return id;
}

function getClientId(): string {
  const clientId = window.localStorage.getItem("housework.x-client-id");
  if (!clientId) return createClientId();
  return clientId;
}

function urlBase64ToUint8Array(base64String: string) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, "+")
    .replace(/_/g, "/");

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function ServiceWorkerListener() {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  useEffect(() => {
    // Define the event listener function
    const handleServiceWorkerMessage = (event: MessageEvent) => {
      if (!event.data.action) {
        return;
      }

      switch (event.data.action) {
        case "goto":
          window.focus();
          dispatch(
            apiService.util.invalidateTags([
              "jobs",
              "notifications",
              "subscriptions",
              "teams",
            ]),
          );
          navigate(event.data.url || "/");
          break;
      }
    };

    if (navigator.serviceWorker) {
      navigator.serviceWorker.addEventListener(
        "message",
        handleServiceWorkerMessage,
      );
    }

    return () => {
      if (navigator.serviceWorker) {
        navigator.serviceWorker.removeEventListener(
          "message",
          handleServiceWorkerMessage,
        );
      }
    };
  }, [dispatch, navigate]);

  return null;
}

function App() {
  const [subscribe] = useSubscribeMutation();
  const { data: selfData } = useGetSelfQuery();

  const notificationPermission = useNotificationPermission();

  const handleSetup = useMemo(() => {
    async function innerHandleSetup() {
      if (notificationPermission === "granted") {
        const sw = await navigator.serviceWorker.ready;
        const subscribeOptions = {
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(
            "BFSP1k6ksWes7cFHVHbdDgl_zJPCwrIbXZVnzEHgWSK9aeDbOzX0rNHIBEaWxAZrBdcVZKZdnPFe7i1mCs2nppI",
          ),
        };

        const sub = await sw.pushManager.subscribe(subscribeOptions);
        try {
          await subscribe({
            channel_type: "BRW_PSH",
            config: JSON.parse(JSON.stringify(sub)),
            name: getClientId(),
            enabled: true,
          }).unwrap();
        } catch (e) {}
      }
    }
    if (selfData) return () => {};
    return debounce(innerHandleSetup, 500);
  }, [selfData, subscribe, notificationPermission]);

  useEffect(() => {
    if (notificationPermission === "granted") handleSetup();
  }, [notificationPermission, handleSetup]);
  return (
    <>
      <AuthWall>
        <Router>
          <ServiceWorkerListener />
          <Routes>
            <Route path="/" element={<Site />} />
            <Route
              path="/notification/:notificationId"
              element={<NotificationRedirect />}
            />
            <Route path="/:section?/:subsection?/" element={<Site />} />
          </Routes>
        </Router>
      </AuthWall>
    </>
  );
}

export default App;
