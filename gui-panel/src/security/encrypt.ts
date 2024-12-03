import crypto from 'crypto';

const algorithm = 'aes-256-cbc';
const key = crypto.randomBytes(32); // Substitute with your own key
const iv = crypto.randomBytes(16);

export const encryptData = (data: string): string => {
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  const encrypted = Buffer.concat([cipher.update(data), cipher.final()]);
  return `${iv.toString('hex')}:${encrypted.toString('hex')}`;
};
