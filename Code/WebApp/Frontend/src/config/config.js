import axios from "axios";

export const base_url = "https://southwest-properties-5b91f978d0cd.herokuapp.com";

export const instance = axios.create({
  // Configuration
  baseURL: base_url,
  timeout: 8000,
  headers: {
    Accept: "application/json",
  },
});
