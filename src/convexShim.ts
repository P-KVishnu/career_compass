// src/convexShim.ts
// Lightweight mock of Convex React Client and hooks
// This lets the app run even without a real Convex backend.

import { useState, useEffect } from "react";

// Simple fake Convex client
export class ConvexReactClient {
  url: string;

  constructor(url: string) {
    this.url = url;
  }

  auth = {
    getUser: () => {
      const user = localStorage.getItem("user");
      return user ? JSON.parse(user) : null;
    },
    signIn: (email: string) => {
      localStorage.setItem("user", JSON.stringify({ email }));
      return { success: true, email };
    },
    signOut: () => {
      localStorage.removeItem("user");
      return { success: true };
    },
  };

  query = async (name: string, ...args: any[]) => {
    console.log(`Fake query: ${name}`, args);
    return null;
  };

  mutation = async (name: string, ...args: any[]) => {
    console.log(`Fake mutation: ${name}`, args);
    return { success: true };
  };
}

// ---- Fake Convex Hooks ----

// Simulate a data mutation
export function useMutation(name: string) {
  return async (...args: any[]) => {
    console.log(`Fake useMutation called: ${name}`, args);
    return { success: true };
  };
}

// Simulate a data query
export function useQuery(name: string, ...args: any[]) {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    console.log(`Fake useQuery triggered: ${name}`, args);
    // Return static demo data
    setData({ message: `Query ${name} resolved` });
  }, [name]);

  return data;
}

// Simulate Convex authentication
export function useConvexAuth() {
  const [isAuthenticated, setAuthenticated] = useState(
    !!localStorage.getItem("user")
  );

  const signIn = (email: string) => {
    localStorage.setItem("user", JSON.stringify({ email }));
    setAuthenticated(true);
  };

  const signOut = () => {
    localStorage.removeItem("user");
    setAuthenticated(false);
  };

  return {
    isAuthenticated,
    signIn,
    signOut,
  };
}
