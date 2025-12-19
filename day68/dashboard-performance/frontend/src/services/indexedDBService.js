import Dexie from 'dexie';

const db = new Dexie('DashboardCache');

db.version(1).stores({
  cache: 'key, data, timestamp, ttl'
});

export const initDB = async () => {
  await db.open();
};

export const getCachedData = async (key) => {
  try {
    const item = await db.cache.get(key);
    
    if (!item) return null;
    
    // Check if expired
    if (Date.now() - item.timestamp > item.ttl) {
      await db.cache.delete(key);
      return null;
    }
    
    return item;
  } catch (error) {
    console.error('IndexedDB get error:', error);
    return null;
  }
};

export const setCachedData = async (key, data, ttl = 300000) => {
  try {
    await db.cache.put({
      key,
      data,
      timestamp: Date.now(),
      ttl
    });
  } catch (error) {
    console.error('IndexedDB set error:', error);
  }
};

export const clearCache = async () => {
  await db.cache.clear();
};
