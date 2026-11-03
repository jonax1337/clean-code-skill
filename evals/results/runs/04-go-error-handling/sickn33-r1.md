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
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		return 0, fmt.Errorf("parse user id: %w", err)
	}
	return id, nil
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

Imports needed: `errors`, `fmt`, `encoding/json`, `log`, `net/http`, `strconv`, and your `store` package.

**What changed**

- **The ignored `Atoi` error is handled.** A missing or malformed `id` used to silently become `0` and hit the database. It now returns `400`.
- **`FindUser` failures stop the handler.** Before, the error was logged and the handler carried on, encoding a zero-value `user` with a `200`. Now it returns early.
- **Errors map to statuses.** `store.ErrNotFound` (matched with `errors.Is`, so it also works if wrapped) becomes `404`. Anything else becomes `500`.
- **Internal details stay out of the response.** The real error is logged with context (`find user 42: ...`), and the client only sees a generic message.
- **The encode error is no longer dropped.** It's logged, not turned into a second `http.Error`, because the status and part of the body may already be written by then.
- **The handler reads top-down.** Parsing and error-to-status mapping live in small helpers, so each function does one thing.

**Behavior changes to be aware of**

Clients that relied on getting `200` with an empty or zero user for bad or unknown IDs will now get `400` or `404`. I also added the `Content-Type: application/json` header. If you have existing callers or tests, check them.

**Suggested tests** (table-driven with `httptest`): a missing id, a non-numeric id, `ErrNotFound`, a generic DB error, and the success case. Each should assert the status code.