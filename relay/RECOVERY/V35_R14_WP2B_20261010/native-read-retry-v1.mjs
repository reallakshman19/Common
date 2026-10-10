/* WP2-B native-read smoke orchestration only: no source attestation,
 * evidence admission, DELP projection, permission, reviewer or writer authority.
 * A bounded retry never changes any native source result or its classification.
 */
export async function observeNativeWithUnknownRetry(locator, read, record = console.log) {
  if (typeof read !== 'function' || typeof record !== 'function')
    throw new TypeError('NATIVE_READ_OR_LOGGER_REQUIRED');
  let result;
  for (let attempt = 1; attempt <= 2; attempt++) {
    result = await read(locator);
    if (!result || typeof result !== 'object' || Array.isArray(result) ||
        typeof result.source_status !== 'string')
      throw new TypeError('NATIVE_READ_RESULT_INVALID');
    // Log the complete observation, including UNKNOWN, before any retry.
    // The helper-owned audit sequence must not be overwritten by a source field.
    record(JSON.stringify({...result, native_read_attempt: attempt}, null, 2));
    if (result.source_status !== 'UNKNOWN') break;
  }
  return result;
}
