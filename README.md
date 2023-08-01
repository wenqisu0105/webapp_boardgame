Areas for improvement:
Storing the game state (including the chess_board) between requests can be a bit tricky as HTTP is a stateless protocol. 

There are several ways to manage this, depending on your exact requirements. Here are a few options:

1. Store in a database: In a typical production application, you might store the game state in a database. Whenever a move is made, you would update the database. This would allow you to easily handle things like users disconnecting and reconnecting, or even switching devices.

2. Send back and forth: Another option is to send the entire game state back to the client after each move, and then have the client send it back again with the next move. This means you don't have to store anything on the server, but it does put more network load on the client and server.

3. Cookies or Session: Yet another option is to use HTTP cookies or sessions to store the state. This is similar to the in-memory option, but takes advantage of built-in HTTP features to do it.