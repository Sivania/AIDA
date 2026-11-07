import type { CSSProperties } from "react";
import type { AssistantState } from "../types/chat";
import "./AidaLogo.css";

interface AidaLogoProps {
  state?: AssistantState;
  size?: number;
  faded?: boolean;
  animated?: boolean;
}

/**
 * AIDA's animated avatar is ONE outlined triangle, not the AIDA wordmark.
 * - idle: slow breathing
 * - thinking: shrink / spin / grow / stop / repeat
 * - responding: breathe with staggered outward speaking waves
 */
export default function AidaLogo({
  state = "idle",
  size = 260,
  faded = false,
  animated = true,
}: AidaLogoProps) {
  const style: CSSProperties = {
    width: `min(${size}px, 100%)`,
  };

  return (
    <div
      className={[
        "aida-logo",
        `aida-logo--${state}`,
        faded && "aida-logo--faded",
        !animated && "aida-logo--static",
      ]
        .filter(Boolean)
        .join(" ")}
      style={style}
      role="img"
      aria-label="AIDA triangle"
    >
      <svg viewBox="0 0 260 220" aria-hidden="true" focusable="false">
        {[1, 2, 3].map((wave) => (
          <path
            key={wave}
            className={`aida-logo__wave aida-logo__wave--${wave}`}
            d="M130 43 L218 178 H42 Z"
          />
        ))}
        <path
          className="aida-logo__core"
          d="M130 43 L218 178 H42 Z"
        />
      </svg>
    </div>
  );
}
