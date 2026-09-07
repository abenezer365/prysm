import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import App from "./app";
import { Toaster } from "sonner";
import "./styles/index.css";
import "./styles/task13.css";
import "./styles/task14.css";
import "./styles/phase6.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <App />
          <Toaster
            position="bottom-right"
            richColors
            closeButton
            expand
            visibleToasts={4}
            duration={4200}
            offset={24}
            toastOptions={{ className: "prysm-toast" }}
          />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
