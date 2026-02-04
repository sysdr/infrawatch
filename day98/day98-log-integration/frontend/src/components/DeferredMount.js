/**
 * Renders children only after a delay.
 * Use to avoid React Strict Mode double-mount closing WebSockets before they connect.
 */
import React, { useState, useEffect } from 'react';

export default function DeferredMount({ children, delay = 100 }) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const id = setTimeout(() => setShow(true), delay);
    return () => clearTimeout(id);
  }, [delay]);

  return show ? children : null;
}
