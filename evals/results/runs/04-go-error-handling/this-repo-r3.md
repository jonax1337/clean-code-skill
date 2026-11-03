```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
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

You'll need `errors` in the imports.

**What was wrong**
- `strconv.Atoi`'s error was discarded, so a missing or malformed `id` silently became `0` and was looked up as a real user.
- A `FindUser` failure was logged, but the handler carried on and encoded a zero-value `user` with a 200 status. Clients couldn't tell "not found" from success.
- The `Encode` error was ignored.

**What it does now**
- A bad `id` gives 400.
- `store.ErrNotFound` gives 404. I used `errors.Is` so it still matches if the store wraps the error.
- Any other `FindUser` error is logged with the operation and id, and the client gets a generic 500, so internals aren't leaked.
- If encoding fails, the status line is already sent and can't change, so the error is only logged with context.
- I added the `Content-Type: application/json` header, since the body is JSON.

**Behavior change:** the endpoint used to return 200 in every case. Clients that relied on that will now see 400, 404 or 500.

**Not done:** I couldn't run or compile anything here, so this is untested. If your codebase already has a helper for error responses (JSON error bodies, a logger other than `log`), use it in place of `http.Error` and `log.Printf` to stay consistent. I'd cover this with handler tests for a non-numeric id, a missing id, `ErrNotFound`, a generic DB error and the success case. I haven't seen your existing tests, so I didn't add any.