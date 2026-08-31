import { Moon, Sun } from "lucide-react";
import { useTheme } from "../context/ThemeContext";
export default function ThemeButton() {
  const { theme, toggle } = useTheme(),
    dark = theme === "dark",
    Icon = dark ? Sun : Moon;
  return (
    <button
      className="button button-ghost !p-2.5"
      onClick={toggle}
      aria-label={`Use ${dark ? "light" : "dark"} theme`}
      title={`Switch to ${dark ? "light" : "dark"} theme`}
    >
      <Icon size={18} />
    </button>
  );
}
