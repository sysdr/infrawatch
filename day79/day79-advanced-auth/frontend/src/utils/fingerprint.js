import Fingerprint2 from 'fingerprintjs2';

export const generateFingerprint = async () => {
  return new Promise((resolve) => {
    Fingerprint2.get((components) => {
      const values = components.map(component => component.value);
      const fingerprint = {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        screen: `${screen.width}x${screen.height}x${screen.colorDepth}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        components: values
      };
      resolve(fingerprint);
    });
  });
};
