/* InfraWatch Service Worker — Day 130 */
const CACHE = 'infrawatch-v130';
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/','/index.html']))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(self.clients.claim()); });

self.addEventListener('push', event => {
  let d = {};
  try { d = event.data ? event.data.json() : {}; } catch(e) { d = {title:'InfraWatch',body:event.data?.text()||''}; }
  event.waitUntil(
    self.registration.showNotification(d.title||'InfraWatch', {
      body: d.body||'New notification', icon: d.icon||'/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png', tag: d.tag||'infrawatch', renotify: true,
      data: {url: d.url||'/', notificationId: d.id},
      actions: [{action:'view',title:'View Dashboard'},{action:'dismiss',title:'Dismiss'}]
    }).then(() => reportEvent(d.id,'delivered'))
  );
});

self.addEventListener('notificationclick', event => {
  const {notification:{data:nd={},close}, action} = event;
  notification.close();
  if (action === 'dismiss') { event.waitUntil(reportEvent(nd.notificationId,'dismissed')); return; }
  event.waitUntil(reportEvent(nd.notificationId,'clicked').then(() =>
    self.clients.matchAll({type:'window',includeUncontrolled:true}).then(cls => {
      for (const c of cls) if ('focus' in c) return c.focus();
      return self.clients.openWindow(nd.url||'/');
    })
  ));
});

self.addEventListener('notificationclose', event => {
  event.waitUntil(reportEvent((event.notification.data||{}).notificationId,'dismissed'));
});

async function reportEvent(id, type) {
  if (!id) return;
  try { await fetch('/api/notifications/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({notification_id:id,event_type:type})}); } catch(_) {}
}

self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(fetch(event.request).catch(()=>new Response('{"error":"offline"}',{headers:{'Content-Type':'application/json'}})));
    return;
  }
  event.respondWith(caches.match(event.request).then(c => c || fetch(event.request)));
});
