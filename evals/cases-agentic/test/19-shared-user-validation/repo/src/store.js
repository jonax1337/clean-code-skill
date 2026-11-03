export function createStore() {
  const users = new Map();
  const invitations = [];
  let nextUserId = 1;
  let nextInvitationId = 1;

  return {
    listUsers() {
      return [...users.values()];
    },
    getUser(id) {
      return users.get(id);
    },
    findUserByEmail(email) {
      return [...users.values()].find((user) => user.email === email);
    },
    addUser(fields) {
      const user = { id: nextUserId++, ...fields };
      users.set(user.id, user);
      return user;
    },
    updateUser(id, changes) {
      const user = { ...users.get(id), ...changes };
      users.set(id, user);
      return user;
    },
    removeUser(id) {
      users.delete(id);
    },
    findInvitationByEmail(email) {
      return invitations.find((invitation) => invitation.email === email);
    },
    addInvitation(fields) {
      const invitation = { id: nextInvitationId++, ...fields, status: 'pending' };
      invitations.push(invitation);
      return invitation;
    },
  };
}
