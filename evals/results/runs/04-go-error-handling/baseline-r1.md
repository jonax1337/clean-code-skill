```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid or missing user id", http.StatusBadRequest)
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

- **Parse error no longer ignored.** A missing or non-numeric `id` previously became `0` silently; now it returns `400 Bad Request`.
- **Early returns on error.** Before, a failed lookup was logged but the handler still encoded a zero/nil `user` with a 200 status.
- **`ErrNotFound` maps to 404** via `errors.Is` (works even if the error is wrapped). Any other error is logged with context and returns a generic 500, so internal details aren't leaked to the client.
- **Content-Type set** to `application/json` before writing the body.
- **Encode error is logged.** Once encoding starts the status is already sent, so logging is all that can be done there.

You'll need to import `errors` and your `store` package. If you want to reject non-positive IDs, add `|| id <= 0` to the parse check.