Here's a cleaned-up version:

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
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

- **Atoi error is no longer ignored.** A missing or malformed `id` previously became `0` and silently queried the wrong user. It now returns `400 Bad Request`.
- **Early returns on failure.** Previously the handler logged the error and then encoded a nil/zero `user` as a `200 OK`. Now each error path responds and returns.
- **`ErrNotFound` maps to 404** via `errors.Is`, which also works if the error is wrapped.
- **Other errors map to 500**, logged with context on the server side, while the client only sees a generic message so internals don't leak.
- **Encode error is checked.** At that point headers are already sent, so all you can do is log it.
- **`Content-Type` is set** to `application/json` before writing the body.

Imports needed: `errors`, `encoding/json`, `log`, `net/http`, `strconv`, and your `store` package.

If you want JSON-formatted error bodies instead of plain text from `http.Error`, I can add a small `writeError(w, status, msg)` helper.