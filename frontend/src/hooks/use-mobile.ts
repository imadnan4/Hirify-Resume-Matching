import * as React from "react";

const DEFAULT_MOBILE_BREAKPOINT = 768;

export function useIsMobile(breakpoint: number = DEFAULT_MOBILE_BREAKPOINT) {
  const [isMobile, setIsMobile] = React.useState(() => {
    if (typeof window === "undefined") return false;
    return window.innerWidth < breakpoint;
  });

  React.useEffect(() => {
    if (typeof window === "undefined") return;

    const mediaQuery = window.matchMedia(`(max-width: ${breakpoint - 1}px)`);

    const onChange = () => setIsMobile(mediaQuery.matches);
    onChange();

    if (typeof mediaQuery.addEventListener === "function") {
      mediaQuery.addEventListener("change", onChange);
      return () => mediaQuery.removeEventListener("change", onChange);
    }

    // Safari < 14
    // eslint-disable-next-line deprecation/deprecation
    mediaQuery.addListener(onChange);
    // eslint-disable-next-line deprecation/deprecation
    return () => mediaQuery.removeListener(onChange);
  }, [breakpoint]);

  return isMobile;
}
