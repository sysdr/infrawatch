/**
 * Run before React loads. Suppresses "Download the React DevTools" in the console.
 */
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  const skip = (args) => {
    const s = args[0] != null ? String(args[0]) : '';
    return s.includes('React DevTools') || s.includes('reactjs.org/link/react-devtools');
  };
  ['log', 'info'].forEach((method) => {
    const orig = console[method];
    if (orig) console[method] = (...args) => { if (skip(args)) return; orig.apply(console, args); };
  });
}
