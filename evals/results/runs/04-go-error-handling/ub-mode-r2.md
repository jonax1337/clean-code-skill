I couldn't run anything here, so none of this has been run. Following ub-mode, the test comes first.

## 1. Failing test (written first)

This assumes `s.db` is an interface, so a fake can stand in for it. I don't know your `Server` or `User` type names, so adjust `Server{db: ...}` and `store.User` to match.

```go
type fakeDB struct {
	user store.User
	err  error
}

func (f fakeDB) FindUser(ctx context.Context, id int) (store.User, error) {
	return f.user, f.err
}

func TestHandleGetUser(t *testing.T) {
	tests := []struct {
		name  string
		query string
		db    fakeDB
		want  int
	}{
		{"found", "?id=1", fakeDB{user: store.User{}}, http.StatusOK},
		{"missing id", "", fakeDB{}, http.StatusBadRequest},
		{"non-numeric id", "?id=abc", fakeDB{}, http.StatusBadRequest},
		{"not found", "?id=1", fakeDB{err: store.ErrNotFound}, http.StatusNotFound},
		{"wrapped not found", "?id=1", fakeDB{err: fmt.Errorf("q: %w", store.ErrNotFound)}, http.StatusNotFound},
		{"db failure", "?id=1", fakeDB{err: errors.New("boom")}, http.StatusInternalServerError},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			s := &Server{db: tc.db}
			rec := httptest.NewRecorder()
			s.handleGetUser(rec, httptest.NewRequest(http.MethodGet, "/user"+tc.query, nil))
			if rec.Code != tc.want {
				t.Fatalf("status = %d, want %d", rec.Code, tc.want)
			}
		})
	}
}
```

With the current handler, every case except "found" fails. It returns 200 with a zero-value user, and the bad id silently becomes 0.

## 2. Smallest change that makes it pass

```go
func (s *Server) handleGetUser(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "invalid id", http.StatusBadRequest)
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

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(user); err != nil {
		log.Printf("encode user %d: %v", id, err)
	}
}
```

## What changed and why

- **Input is checked where it enters.** `Atoi`'s error was discarded, so `?id=abc` silently looked up user 0. It now returns 400.
- **Not found returns 404.** It uses `errors.Is`, so wrapped errors still match.
- **Other DB errors return 500.** The error is logged with context, and the client gets a generic message, so internals don't leak. Before, the error was logged but the handler continued and returned 200 with an empty user.
- **Each failure path returns.** That fixes the root cause rather than hiding it.
- **The encode error is logged.** The status is already sent by then, so logging is all that's left to do. I also set `Content-Type`.

## Log

1. Wrote a table test covering each failure mode, to pin the intended behavior before changing code.
2. Moved id parsing to the top and rejected bad input with 400.
3. Split the DB error handling into not-found (404) and everything else (500), with an early return on both.
4. Handled the encode error and set the content type.

I did not run the crapper, dryer or mutator tools, and nothing was committed, because I have no tool access in this session. The handler has low branching, so CRAP should stay well under 10 once the test above is in place.