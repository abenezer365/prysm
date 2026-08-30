import { createContext, useContext, useEffect, useState } from 'react';
const ThemeContext=createContext(null); const themes=['light','warm','dark'];
export function ThemeProvider({children}){const[theme,setTheme]=useState(()=>localStorage.getItem('prysm-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));useEffect(()=>{document.documentElement.dataset.theme=theme;localStorage.setItem('prysm-theme',theme)},[theme]);const toggle=()=>setTheme(current=>themes[(themes.indexOf(current)+1)%themes.length]);return <ThemeContext.Provider value={{theme,setTheme,toggle,themes}}>{children}</ThemeContext.Provider>}
export const useTheme=()=>useContext(ThemeContext);
