# Error handling in Go

Tests: language idioms over book rules, no swallowed errors, errors with context.

## Prompt

Make the error handling in this handler clean.

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, _ := strconv.Atoi(r.URL.Query().Get("id"))
	user, err := s.db.FindUser(r.Context(), id)
	if err != nil {
		log.Println(err)
	}
	json.NewEncoder(w).Encode(user)
}
```

`s.db.FindUser` returns `store.ErrNotFound` when no user exists.

## Assertions

1. An invalid or missing `id` is detected (the `Atoi` error is checked) and answered with HTTP 400.
2. On a lookup error the handler returns instead of continuing; `store.ErrNotFound` is distinguished with `errors.Is` and mapped to 404, other errors to 500.
3. Idiomatic Go: plain `error` values; no `panic`/`recover` for control flow and no exception-like wrapper types invented.
4. Logged errors carry context (operation and/or id), and internal error details are not written to the client response.
5. The `Encode` error is handled or explicitly addressed.
