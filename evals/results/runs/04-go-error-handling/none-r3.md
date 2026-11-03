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

What changed:

- **Parse error is checked.** Previously `Atoi` failures silently became `id = 0`. Now a bad or missing id returns `400`.
- **Early returns on error.** The original logged the error but then still encoded `user` (likely a zero value or nil) with a 200 status.
- **`ErrNotFound` maps to `404`**, using `errors.Is` so it still matches if the store wraps the error.
- **Other errors return `500`** with a generic message; details are logged server-side with context, not leaked to the client.
- **Encode error is handled.** Once encoding starts, headers may already be sent, so we can only log it rather than write another status.
- **`Content-Type: application/json`** is set explicitly.

You'll need `errors` imported alongside the existing imports. If you want to go further, a small helper like `writeError(w, status, msg)` (or JSON-formatted error bodies) would cut the repetition across handlers.