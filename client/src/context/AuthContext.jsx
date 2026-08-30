import { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../services/api';
const AuthContext=createContext(null); const KEY='prysm-access-token';
export function AuthProvider({children}) { const [token,setToken]=useState(()=>sessionStorage.getItem(KEY)); const [user,setUser]=useState(null); const [permissions,setPermissions]=useState([]); const [clearance,setClearance]=useState(null); const [loading,setLoading]=useState(Boolean(token));
  useEffect(()=>{ if(!token){setLoading(false);return} let active=true; Promise.all([api.me(token),api.permissions(token),api.clearance(token)]).then(([u,p,c])=>{if(active){setUser(u);setPermissions(p.permissions||[]);setClearance(c.rank)}}).catch(()=>{if(active){sessionStorage.removeItem(KEY);setToken(null)}}).finally(()=>active&&setLoading(false)); return()=>{active=false}},[token]);
  async function login(credentials){const result=await api.login(credentials); const access=result.accessToken || result.access?.token; if(!access) throw new Error('The backend did not return an access token.'); sessionStorage.setItem(KEY,access); setToken(access); setLoading(true); return result}
  async function logout(){try{if(token)await api.logout(token)}finally{sessionStorage.removeItem(KEY);setToken(null);setUser(null);setPermissions([]);setClearance(null)}}
  return <AuthContext.Provider value={{token,user,permissions,clearance,loading,login,logout,can:p=>permissions.includes(p)}}>{children}</AuthContext.Provider> }
export const useAuth=()=>useContext(AuthContext);
