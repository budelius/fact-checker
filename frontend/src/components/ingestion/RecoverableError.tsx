export function RecoverableError({ error }: { error: string }) {
  return (
    <div className="recoverable-error" role="alert">
      This video could not be processed. Check that the link is public, try another URL, upload
      another video, or use the pasted-transcript fallback. {error}
    </div>
  );
}
