import * as React from 'react';

declare global {
  interface Window {
    __originalCSS?: string;
  }
}

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'el-dialog': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
      'el-dialog-panel': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
      'el-disclosure': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
        open?: boolean | string;
        hidden?: boolean | string;
      };
    }
  }

  interface ButtonHTMLAttributes<T> extends React.HTMLAttributes<T> {
    command?: string;
    commandfor?: string;
  }
}
