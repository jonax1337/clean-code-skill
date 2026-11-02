Here's a cleaned-up version:

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid or missing id", http.StatusBadRequest)
		return
	}

	user, err := s.db.FindUser(r.Context(), id)
	if err != nil {
		if errors.Is(err, store.ErrNotFound) {
			http.Error(w, "user not found", http.StatusNotFound)
			return
		}
		log.Printf("handleGetUser: find user %d: %v", id, err)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(user); err != nil {
		log.Printf("handleGetUser: encode response for user %d: %v", id, err)
	}
}
```

Add `"errors"` to your imports.

What changed:

- **Parse errors are handled.** The original discarded the `Atoi` error, so a bad or missing `id` silently became `0`. It now returns `400`.
- **Early returns on failure.** Previously, after logging a `FindUser` error the handler still encoded `user` and returned a `200`. Now it stops.
- **`ErrNotFound` maps to `404`.** It's checked with `errors.Is`, so it still matches if the error is wrapped.
- **Other errors return `500`.** The details are logged server-side with context, and the client gets a generic message so internals don't leak.
- **Content-Type is set** to `application/json` before writing the body.
- **Encode error is logged.** At that point the status is already sent, so logging is all you can do.

If your project returns JSON errors rather than plain text, swap `http.Error` for a small helper like `writeError(w, status, msg)` that encodes `{"error": msg}`.