export function mayDisplay(selected, completed) {
  return selected.revision === completed.revision;
}
