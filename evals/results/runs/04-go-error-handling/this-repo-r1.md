```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
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
		log.Printf("get user %d: %v", id, err)
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}

	if err := json.NewEncoder(w).Encode(user); err != nil {
		log.Printf("get user %d: encode response: %v", id, err)
	}
}
```

You'll need `errors` in the imports (`store` is already imported, since you reference `store.ErrNotFound`).

**What was wrong and what changed**

- **Ignored `Atoi` error:** `?id=abc` or a missing id silently became `0` and was looked up as a real user. It now returns 400.
- **Log-and-continue after `FindUser` fails:** the handler went on to encode a zero or nil `user` with a 200 status. Every failure now returns early.
- **`ErrNotFound` is distinguished from other errors:** not found returns 404 (matched with `errors.Is`, so wrapped errors work). Anything else returns 500.
- **Internal errors stay out of the response:** the client gets a generic message, and the real error is logged with the operation and the id, so the log line is useful.
- **Unchecked `Encode` error:** it is now logged. The status line is already sent at that point, so logging is all that can be done.

**Behavior change:** callers that previously always got a 200 now get 400, 404 or 500 in those cases. Any client relying on the old behavior will notice.

I did not run or compile this, and I have not seen your tests. If the handler has tests, they need cases for a bad id, `ErrNotFound`, another DB error and the success path.

I left out setting `Content-Type: application/json` on success, since it is outside error handling. It's worth adding in a separate change.