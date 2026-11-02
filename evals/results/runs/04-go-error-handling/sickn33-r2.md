```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := parseUserID(r)
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
		return
	}

	user, err := s.db.FindUser(r.Context(), id)
	if errors.Is(err, store.ErrNotFound) {
		http.Error(w, "user not found", http.StatusNotFound)
		return
	}
	if err != nil {
		log.Printf("find user %d: %v", id, err)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	writeJSON(w, user)
}

func parseUserID(r *http.Request) (int, error) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		return 0, fmt.Errorf("parse user id: %w", err)
	}
	return id, nil
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(v); err != nil {
		log.Printf("encode response: %v", err)
	}
}
```

Imports needed: `errors`, `fmt`, `encoding/json`, `log`, `net/http`, `strconv`, plus your `store` package.

**What changed and why**

- **Atoi error no longer discarded.** A missing or malformed `id` used to silently become `0` and query the wrong user. It now returns `400 Bad Request`.
- **Early returns on every failure.** Before, the handler logged the DB error and then encoded a zero-value `user` anyway, so clients got a `200` with bogus data.
- **`errors.Is(err, store.ErrNotFound)` maps to `404`.** This works even if the DB layer wraps the error. Any other error is logged with context and returned as a generic `500`, so internals don't leak to the client.
- **Small helpers.** `parseUserID` and `writeJSON` keep the handler at one level of abstraction. It reads as: parse, find, respond.
- **Encode errors are logged, not ignored.** Once the body has started, the status can't change, so logging is all that's useful.

**Behavior changes to be aware of:** clients now get real status codes (`400`, `404`, `500`) instead of always `200`, and responses carry `Content-Type: application/json`. If any callers relied on the old behavior, check them. I haven't run this, so a handler test for each of the four paths (bad id, not found, internal error, success) would be the right way to verify it.