Three bugs were hiding behind the "error handling" here:

- The `Atoi` error was discarded, so `?id=abc` silently looked up user 0.
- A `FindUser` error was logged, but the handler then encoded a nil or zero user and returned 200.
- `ErrNotFound` was indistinguishable from a real failure.

I couldn't run anything in this session, so the test and handler below are untested. The test comes first, as the skill requires.

## 1. Failing test first

I assumed `s.db` is an interface that can be faked, and that `FindUser` returns `(*store.User, error)`. Adjust the fake to your real signature.

```go
type fakeDB struct {
	user *store.User
	err  error
}

func (f fakeDB) FindUser(ctx context.Context, id int) (*store.User, error) {
	return f.user, f.err
}

func TestHandleGetUser_StatusCodes(t *testing.T) {
	cases := []struct {
		name  string
		query string
		db    fakeDB
		want  int
	}{
		{"found", "?id=1", fakeDB{user: &store.User{}}, http.StatusOK},
		{"missing id", "", fakeDB{}, http.StatusBadRequest},
		{"non-numeric id", "?id=abc", fakeDB{}, http.StatusBadRequest},
		{"not found", "?id=1", fakeDB{err: store.ErrNotFound}, http.StatusNotFound},
		{"wrapped not found", "?id=1", fakeDB{err: fmt.Errorf("lookup: %w", store.ErrNotFound)}, http.StatusNotFound},
		{"db failure", "?id=1", fakeDB{err: errors.New("boom")}, http.StatusInternalServerError},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			s := &Server{db: tc.db}
			rec := httptest.NewRecorder()
			req := httptest.NewRequest(http.MethodGet, "/user"+tc.query, nil)

			s.handleGetUser(rec, req)

			if rec.Code != tc.want {
				t.Fatalf("got status %d, want %d", rec.Code, tc.want)
			}
		})
	}
}
```

Against the current handler, every case except "found" fails because it always returns 200. That is the failure I expect.

## 2. Smallest change that passes

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
		http.Error(w, "internal error", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(user); err != nil {
		log.Printf("encode user %d: %v", id, err)
	}
}
```

- **Input is validated at the boundary.** A bad `id` gets a 400, and the rest of the handler trusts it.
- **`errors.Is`** matches `ErrNotFound` even when it has been wrapped.
- **Internal errors are logged, not leaked.** The client sees a generic 500, and the detail goes to the log with the user id for context.
- **Every error path returns.** Nothing falls through to encode a nil user.
- **Encode failures are logged.** Once the body has started, the status can't change, so logging is all that can be done.

## Action log

1. Identified the root causes: the ignored `Atoi` error, the missing early return, and no distinction for `ErrNotFound`.
2. Wrote a table-driven test that checks the status code a caller would see, including a wrapped `ErrNotFound`.
3. Made the smallest handler change to satisfy it.

## Not done yet

- **Test run:** run the test, and confirm it fails against the old handler and passes against the new one.
- **Crapper, dryer and mutator:** the skill's quality tools weren't available here, so I didn't run them. The handler is small and has few branches, so I'd expect it to be well under CRAP 10.
- **Commit and push:** there is no git repo in this directory, so I made no commit.