import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { api, setAccessTokenRenewer } from "../services/api";
const AuthContext = createContext(null),
  KEY = "prysm-access-token",
  REFRESH_KEY = "prysm-refresh-token";
export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => sessionStorage.getItem(KEY)),
    [user, setUser] = useState(null),
    [permissions, setPermissions] = useState([]),
    [clearance, setClearance] = useState(null),
    [loading, setLoading] = useState(Boolean(token)),
    refreshPromise = useRef(null);
  const clearSession = useCallback(() => {
    sessionStorage.removeItem(KEY);
    sessionStorage.removeItem(REFRESH_KEY);
    setToken(null);
    setUser(null);
    setPermissions([]);
    setClearance(null);
  }, []);
  const renewAccessToken = useCallback(() => {
    if (refreshPromise.current) return refreshPromise.current;
    const refreshToken = sessionStorage.getItem(REFRESH_KEY);
    if (!refreshToken) return Promise.reject(new Error("No refresh token is available."));
    refreshPromise.current = api.refresh(refreshToken)
      .then((result) => {
        if (!result.accessToken || !result.refreshToken) throw new Error("The backend returned an incomplete refreshed session.");
        sessionStorage.setItem(KEY, result.accessToken);
        sessionStorage.setItem(REFRESH_KEY, result.refreshToken);
        setToken(result.accessToken);
        return result.accessToken;
      })
      .catch((error) => {
        clearSession();
        throw error;
      })
      .finally(() => { refreshPromise.current = null; });
    return refreshPromise.current;
  }, [clearSession]);
  useEffect(() => {
    setAccessTokenRenewer(renewAccessToken);
    return () => setAccessTokenRenewer(null);
  }, [renewAccessToken]);
  const refreshSession = useCallback(
    async (currentToken = token) => {
      if (!currentToken) return null;
      const [u, p, c] = await Promise.all([
        api.me(currentToken),
        api.permissions(currentToken),
        api.clearance(currentToken),
      ]);
      setUser(u);
      setPermissions(p.permissions || []);
      setClearance(c.rank);
      return u;
    },
    [token],
  );
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    let active = true;
    setLoading(true);
    refreshSession(token)
      .catch(() => {
        if (active) {
          clearSession();
        }
      })
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [token, refreshSession, clearSession]);
  async function login(credentials) {
    const normalizedCredentials = {
        ...credentials,
        email: credentials.email.trim().toLowerCase(),
      },
      result = await api.login(normalizedCredentials),
      access = result.accessToken || result.access?.token;
    if (!access) throw new Error("The backend did not return an access token.");
    sessionStorage.setItem(KEY, access);
    if (result.refreshToken) sessionStorage.setItem(REFRESH_KEY, result.refreshToken);
    setToken(access);
    setLoading(true);
    try {
      await refreshSession(access);
      return result;
    } catch (error) {
      clearSession();
      throw error;
    } finally {
      setLoading(false);
    }
  }
  async function logout() {
    try {
      if (token) await api.logout(token);
    } finally {
      clearSession();
    }
  }
  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        permissions,
        clearance,
        loading,
        login,
        logout,
        refreshSession,
        can: (p) => permissions.includes(p),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
export const useAuth = () => useContext(AuthContext);
