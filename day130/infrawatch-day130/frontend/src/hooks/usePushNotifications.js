import { useState, useCallback } from 'react';
import { vapidApi, subscriptionsApi } from '../services/api.js';

function urlBase64ToUint8Array(b64) {
  const pad = '='.repeat((4 - b64.length % 4) % 4);
  const b = (b64 + pad).replace(/-/g, '+').replace(/_/g, '/');
  return Uint8Array.from([...window.atob(b)].map(c => c.charCodeAt(0)));
}

export function usePushNotifications() {
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);

  const subscribe = useCallback(async (userId) => {
    setStatus('requesting'); setError(null);
    try {
      if (!('Notification' in window))    throw new Error('Notifications not supported');
      if (!('serviceWorker' in navigator)) throw new Error('Service Worker not supported');
      if (!('PushManager' in window))      throw new Error('Push API not supported');

      const perm = await Notification.requestPermission();
      if (perm !== 'granted') { setStatus('denied'); return null; }

      const { data: vk } = await vapidApi.getPublicKey();
      if (!vk.public_key) throw new Error('VAPID public key not configured');

      const reg = await navigator.serviceWorker.ready;
      const ps  = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: urlBase64ToUint8Array(vk.public_key) });
      const sub = ps.toJSON();

      const { data } = await subscriptionsApi.create({
        user_id: userId, endpoint: sub.endpoint,
        keys: { p256dh: sub.keys.p256dh, auth: sub.keys.auth },
        user_agent: navigator.userAgent.slice(0, 200),
      });
      setStatus('subscribed');
      return data;
    } catch (err) { setStatus('error'); setError(err.message); return null; }
  }, []);

  const unsubscribe = useCallback(async (id) => {
    try { await subscriptionsApi.delete(id); setStatus('idle'); }
    catch (err) { setError(err.message); }
  }, []);

  const checkPermission = useCallback(() =>
    ('Notification' in window) ? Notification.permission : 'unsupported', []);

  return { status, error, subscribe, unsubscribe, checkPermission };
}
