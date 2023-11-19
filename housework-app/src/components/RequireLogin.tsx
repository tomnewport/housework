import { useGetSelfQuery } from "../services/housework/auth";
import LoginForm from "./LoginForm";

interface RequireLoginProps {
  children: JSX.Element;
}

export default function RequireLogin({ children }: RequireLoginProps) {
  const {
    data: userData,
    error,
    isLoading,
  } = useGetSelfQuery(undefined, { pollingInterval: 60000 });
  if (isLoading) {
    return <p>Loading...</p>;
  }
  if (userData === null) {
    return <LoginForm open={true} onClose={() => {}} />;
  }
  if (error) {
    return <LoginForm open={true} onClose={() => {}} />;
  }
  return children;
}
