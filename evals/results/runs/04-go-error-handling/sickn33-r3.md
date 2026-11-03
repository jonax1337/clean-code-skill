Here is the refactored handler:

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := parseUserID(r)
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
		return
	}

	user, err := s.db.FindUser(r.Context(), id)
	if err != nil {
		respondWithFindUserError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, user)
}

func parseUserID(r *http.Request) (int, error) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		return 0, fmt.Errorf("parse user id: %w", err)
	}
	return id, nil
}

func respondWithFindUserError(w http.ResponseWriter, err error) {
	if errors.Is(err, store.ErrNotFound) {
		http.Error(w, "user not found", http.StatusNotFound)
		return
	}
	log.Printf("find user: %v", err)
	http.Error(w, "internal server error", http.StatusInternalServerError)
}

func writeJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(body); err != nil {
		log.Printf("write response: %v", err)
	}
}
```

**What was wrong and what changed**

- **Ignored `Atoi` error:** a missing or malformed `id` silently became `0` and was looked up as a real user. It now returns `400`.
- **Logged but continued:** after a `FindUser` failure the old code still encoded the (zero) `user` and replied `200`. Now each failure path returns immediately.
- **`ErrNotFound` handled explicitly:** it's matched with `errors.Is` (so wrapped errors work) and mapped to `404`. Any other error is logged and returned as a generic `500`, so internal details don't leak to the client.
- **Encode error no longer dropped:** it is logged. The status is already sent by then, so logging is all that can be done.
- **Small, single-level functions:** the handler reads as a top-down narrative (parse, find, respond), with the details pushed into helpers.

**Behavior changes to be aware of**

Clients that previously got `200` with a zero-value body on bad input or missing users will now get `400`/`404`/`500`. That's the point of the change, but check for any callers relying on the old behavior. If your repo already has a JSON error format or a shared response helper, swap `http.Error` and `writeJSON` for it to match conventions.

**Suggested tests**

I haven't run anything here, but a table-driven `httptest` test would cover these cases with a fake `db`:

| Case | Expected status |
|---|---|
| `id=abc` or missing | 400 |
| `FindUser` returns `store.ErrNotFound` | 404 |
| `FindUser` returns a wrapped `ErrNotFound` | 404 |
| `FindUser` returns another error | 500 |
| User found | 200 with JSON body |