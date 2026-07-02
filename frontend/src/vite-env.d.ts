/// <reference types="vite/client" />

// Add your custom env vars here so TypeScript knows them.
// Vite only exposes variables prefixed with VITE_.
interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
