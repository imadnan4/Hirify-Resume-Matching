import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import './styles/oatmeal.css';
import '@tailwindplus/elements';

const rootElement = document.getElementById('root');
if (rootElement) {
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
