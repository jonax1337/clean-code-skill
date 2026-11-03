Here's the test first, then the fix. I couldn't run anything here, so the test is unrun and I haven't seen it fail.

## Failing test first

I'm assuming `Server.db` is an interface with `FindUser(ctx, id) (*store.User, error)`. Adjust the fake and constructor to match your code.

```go
type fakeDB struct {
	user *store.User
	err  error
}

func (f fakeDB) FindUser(ctx context.Context, id int) (*store.User, error) {
	return f.user, f.err
}

func TestHandleGetUser(t *testing.T) {
	tests := []struct {
		name string
		url  string
		db   fakeDB
		want int
	}{
		{"ok", "/user?id=1", fakeDB{user: &store.User{}}, http.StatusOK},
		{"missing id", "/user", fakeDB{}, http.StatusBadRequest},
		{"non-numeric id", "/user?id=abc", fakeDB{}, http.StatusBadRequest},
		{"not found", "/user?id=1", fakeDB{err: store.ErrNotFound}, http.StatusNotFound},
		{"wrapped not found", "/user?id=1", fakeDB{err: fmt.Errorf("x: %w", store.ErrNotFound)}, http.StatusNotFound},
		{"db failure", "/user?id=1", fakeDB{err: errors.New("boom")}, http.StatusInternalServerError},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			s := &Server{db: tt.db}
			rec := httptest.NewRecorder()
			s.handleGetUser(rec, httptest.NewRequest(http.MethodGet, tt.url, nil))
			if rec.Code != tt.want {
				t.Fatalf("got %d, want %d", rec.Code, tt.want)
			}
		})
	}
}
```

The current handler returns 200 for every case, so every case except "ok" should fail with the status code mismatch.

## The fix

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

## What was wrong (root causes)

- **Ignored `Atoi` error:** a bad or missing `id` silently became `0` and queried the wrong user. It now returns 400, validated where the input enters.
- **Log-and-continue on a DB error:** the handler went on to encode a nil or zero user and sent 200. It now returns early.
- **No distinction between not found and failure:** `errors.Is(err, store.ErrNotFound)` gives 404 and still matches if the error is wrapped. Anything else is a 500 with a generic message, so internals don't leak to the client. The detail goes to the log.
- **Unchecked `Encode` error:** it is now logged. Headers are already sent at that point, so logging is all that can be done.
- **Missing `Content-Type`:** I set it to `application/json`.

## Log

1. Wrote a table-driven behavior test through `httptest` so it checks what a client sees. Reason: TDD.
2. Made one edit to the handler. Reason: this is the smallest change that fixes all the cases.
3. Left the structure alone. Reason: the function is small and local. Its branching is about CRAP 7 with this test, under the threshold of 10.

## Not done

- The crapper, dryer and mutator tools aren't available in this session, so I haven't run them. The mutation run should cover the `errors.Is` branch in particular.
- This isn't a git repo, so there is no commit or push. A suggested commit message: *"Return proper HTTP status codes from handleGetUser; previously bad ids and DB errors returned 200 with an empty body. Verified by table-driven handler test."*