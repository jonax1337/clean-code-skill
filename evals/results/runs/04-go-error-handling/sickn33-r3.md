Here's the handler with the error paths handled explicitly. I haven't compiled or run it.

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
		return
	}

	user, err := s.db.FindUser(r.Context(), id)
	switch {
	case errors.Is(err, store.ErrNotFound):
		http.Error(w, "user not found", http.StatusNotFound)
		return
	case err != nil:
		log.Printf("find user %d: %v", id, err)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	writeJSON(w, user)
}

func writeJSON(w http.ResponseWriter, value any) {
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(value); err != nil {
		log.Printf("encode response: %v", err)
	}
}
```

You'll need to import `errors`.

**What changed**

- **Ignored `Atoi` error:** a missing or malformed `id` used to become `0` and query the wrong user. It now returns `400`.
- **Logged but not handled:** after a `FindUser` failure the old code still encoded the (nil or zero) user and returned `200`. Each failure now returns early.
- **`store.ErrNotFound`:** checked with `errors.Is`, so it still matches if the store wraps it, and maps to `404`.
- **Other errors:** logged with context (the user id) and returned as a generic `500`, so internal details don't leak to the client.
- **Encode error:** no longer dropped. It can only be logged, since headers are already sent by then. I moved it into `writeJSON`, which also sets `Content-Type`, so the handler stays at one level of abstraction.

**Behavior changes to be aware of:** clients that previously got `200` with an empty or `null` body for a missing user will now get `404`. Bad ids now get `400`. If you have callers or tests relying on the old behavior, they'll need updating. Also, if `id=0` is a legitimate value in your system, this still accepts it. If not, add a check for `id <= 0`.

I'd add table-driven tests with `httptest` covering bad id, `ErrNotFound`, a generic error, and success, using a fake `db`.