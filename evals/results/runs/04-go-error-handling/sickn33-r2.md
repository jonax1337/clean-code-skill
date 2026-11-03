Here's a version that handles each failure explicitly and maps it to the right HTTP status:

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

	writeJSON(w, http.StatusOK, user)
}

func writeJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(body); err != nil {
		log.Printf("write json response: %v", err)
	}
}
```

Imports needed: `errors`, `encoding/json`, `log`, `net/http`, `strconv`, and your `store` package.

**What changed and why**

- **Parse error no longer discarded.** `_` hid bad input, so a missing or malformed `id` silently became `0` and queried the wrong user. It now returns `400`.
- **Early return on lookup failure.** Previously the error was logged and execution continued, so the handler encoded a zero-value or nil `user` as a successful response.
- **`ErrNotFound` is a client condition, not a server fault.** It's matched with `errors.Is` (so wrapped errors still match) and returns `404` without logging noise.
- **Unexpected errors are logged with context and hidden from the client.** The log line includes the operation and ID, and the response is a generic `500` so internals don't leak.
- **Encoding is extracted into `writeJSON`.** This keeps the handler at one level of abstraction, sets the `Content-Type`, and stops ignoring the encoder's error. After the header is written the status can't change, so logging is the only sensible response there.

**Behavior change to be aware of:** the handler used to return `200` in every case. Clients that relied on that will now see `400`, `404`, or `500`.

If the rest of your codebase already has a response or error helper, use that instead of `http.Error` and `writeJSON` to stay consistent. I couldn't run anything here, so I'd cover this with a table-driven `httptest` test with cases for a bad id, `ErrNotFound`, a generic DB error, and success.