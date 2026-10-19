export function redact(input: string): string {
  let value = input;
  for (const [key, secret] of Object.entries(process.env)) {
    if (/(?:KEY|TOKEN|SECRET|PASSWORD|DATABASE_URL)$/i.test(key) && secret && secret.length >= 8) value = value.split(secret).join('[ĐÃ ẨN]');
  }
  return value
    .replace(/AIza[\w-]{20,}/g, '[API KEY ĐÃ ẨN]')
    .replace(/Bearer\s+[\w.\-+/=]+/gi, 'Bearer [ĐÃ ẨN]')
    .replace(/((?:password|api[_-]?key|access[_-]?token|authorization|cookie|set-cookie)\s*[=:]\s*)[^\r\n,;]+/gi, '$1[ĐÃ ẨN]')
    .replace(/\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi, '[EMAIL ĐÃ ẨN]');
}
