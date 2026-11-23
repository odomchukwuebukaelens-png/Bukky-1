import React, { useContext } from "react";

// Which language a humpback composition is in. The Ukrainian video is the default;
// the English video wraps everything in <LangContext.Provider value="en">.
export type Lang = "uk" | "en";
export const LangContext = React.createContext<Lang>("uk");
export const useLang = () => useContext(LangContext);
export const useT = () => {
  const lang = useLang();
  return (uk: string, en: string) => (lang === "en" ? en : uk);
};
