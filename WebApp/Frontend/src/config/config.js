import axios from "axios";

export const base_url = "http://127.0.0.1:5000/";

export const instance = axios.create({
  // Configuration
  baseURL: base_url,
  timeout: 8000,
  headers: {
    Accept: "application/json",
  },
});
