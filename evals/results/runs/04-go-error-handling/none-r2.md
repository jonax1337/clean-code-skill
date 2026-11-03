```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid or missing id", http.StatusBadRequest)
		return
	}

	user, err := s.db.FindUser(r.Context(), id)
	switch {
	case errors.Is(err, store.ErrNotFound):
		http.Error(w, "user not found", http.StatusNotFound)
		return
	case err != nil:
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

- **Atoi error was ignored**: a missing or malformed `id` silently became `0`. It now returns `400 Bad Request`.
- **Not found vs. other errors**: `store.ErrNotFound` maps to `404` via `errors.Is` (works even if the error is wrapped). Any other error is logged with context and returns a generic `500`, so internal details aren't leaked to the client.
- **Early return**: the original logged the error but still encoded `user` (likely a zero value or nil) with a `200`. Now the handler stops after any failure.
- **Encode error**: handled by logging only, since once the body has started writing you can't change the status code.
- **Content-Type**: set to `application/json` before writing the body.

You'll need `errors` imported alongside the existing imports. If you want stricter validation, you could also reject `id <= 0` in the first check.