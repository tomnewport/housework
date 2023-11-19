import { useState, useEffect } from "react";

export const useIsLandscape = (): boolean => {
  const [isLandscape, setIsLandscape] = useState(
    window.innerWidth > 500 && window.innerWidth > window.innerHeight,
  );

  useEffect(() => {
    const handleResize = () =>
      setIsLandscape(
        window.innerWidth > 500 && window.innerWidth > window.innerHeight,
      );
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return isLandscape;
};
