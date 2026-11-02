```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := parseUserID(r)
	if err != nil {
		http.Error(w, "invalid user id", http.StatusBadRequest)
		return
	}

	user, err := s.db.FindUser(r.Context(), id)
	if err != nil {
		writeFindUserError(w, id, err)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(user); err != nil {
		log.Printf("encode user %d: %v", id, err)
	}
}

func parseUserID(r *http.Request) (int, error) {
	return strconv.Atoi(r.URL.Query().Get("id"))
}

func writeFindUserError(w http.ResponseWriter, id int, err error) {
	if errors.Is(err, store.ErrNotFound) {
		http.Error(w, "user not found", http.StatusNotFound)
		return
	}
	log.Printf("find user %d: %v", id, err)
	http.Error(w, "internal server error", http.StatusInternalServerError)
}
```

Imports needed: `encoding/json`, `errors`, `log`, `net/http`, `strconv`, and your `store` package.

**What changed and why**

- **Ignored `Atoi` error:** a missing or malformed `id` silently became `0` and hit the database. It now returns `400`.
- **Logged but not handled `FindUser` error:** the old code logged the error and then encoded a zero-value `user` as a `200`. Now the handler returns early.
- **`store.ErrNotFound`:** checked with `errors.Is` (so it still matches if wrapped) and mapped to `404`.
- **Other errors:** logged with context (operation and id) on the server, and the client gets a generic `500` so internals don't leak.
- **Encode error:** no longer dropped. Since headers are already sent by then, the only sensible action is to log it.
- **Structure:** the handler reads as a top-down narrative (parse, fetch, respond). Parsing and error-to-status mapping live in small single-purpose helpers.
- **Content-Type:** I set `application/json` on the success path, which the original omitted.

**Behavior changes to be aware of:** invalid ids, not-found, and DB failures used to return `200` with a JSON body (`null` or an empty user). They now return `400`, `404`, and `500`. If any clients depended on the old behavior, check them. Also, `id=0` is still accepted as a valid parse; add a range check in `parseUserID` if ids must be positive.

I haven't run this. I'd add table-driven `httptest` cases for a bad id, `ErrNotFound`, a generic DB error, and success.