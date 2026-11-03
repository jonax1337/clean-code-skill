```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid or missing user id", http.StatusBadRequest)
		return
	}

	user, err := s.db.FindUser(r.Context(), id)
	if errors.Is(err, store.ErrNotFound) {
		http.Error(w, "user not found", http.StatusNotFound)
		return
	}
	if err != nil {
		log.Printf("handleGetUser: find user %d: %v", id, err)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(user); err != nil {
		log.Printf("handleGetUser: encode user %d: %v", id, err)
	}
}
```

Needs `errors` imported alongside the existing imports.

What changed:

- **Parse error no longer discarded.** `strconv.Atoi` failed silently and fell through to a lookup of id 0. Now a bad or missing id returns 400.
- **Not found vs. failure.** `store.ErrNotFound` maps to 404 via `errors.Is` (so it still matches if wrapped). Any other error is logged with context (operation and id) and returns a generic 500, so internal details don't leak to the client.
- **Early return.** Previously, after a failed lookup the handler still encoded a nil/zero `user` as a 200 response. It now returns.
- **Encode error handled.** It's logged, not ignored. Headers are already sent at that point, so we can't change the status; logging is the only useful option. I also set `Content-Type: application/json`, which the original omitted.

Not run: I couldn't compile or test this here, and I've only seen this one function. I don't know whether the project has handler tests or a shared error-response helper; if it does, use it instead of `http.Error`. A test per branch (bad id, not found, other DB error, success) using `httptest` would pin this behavior.

One thing I left alone: `id=0` or negative values are passed to the DB as-is. If ids are always positive, you may want to reject those with 400 too.