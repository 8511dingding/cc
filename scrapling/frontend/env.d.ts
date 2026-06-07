export {}

declare global {
  interface Window {
    __env__: {
      API_URL: string
    }
  }
}
