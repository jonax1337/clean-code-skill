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

- **Id parsing**: the ignored `Atoi` error is now checked, so a missing or malformed id returns `400` instead of silently looking up user `0`.
- **Early returns**: previously, after a DB error the handler logged and then encoded a nil/zero `user` as a `200`. Now every error path returns.
- **Not found vs. internal errors**: `store.ErrNotFound` (matched with `errors.Is`, so it works if wrapped) maps to `404`. Anything else is logged with context and returns a generic `500`, so internal details don't leak to the client.
- **Encode error**: it's checked and logged. Since headers are already sent by then, you can't change the status, so logging is all that's useful.
- **Content-Type**: set to `application/json` before writing the body.

You'll need `errors` imported alongside the existing imports. If you want to go further, consider a small helper (e.g. `writeError(w, status, msg)`) that emits JSON error bodies to match your success responses, and use `slog` or your request-scoped logger instead of `log.Printf`.