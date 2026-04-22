# Tutorial 2: Connecting to SQLite Databases

EPL doesn't just do web routing—it also has first-class integration with SQLite built directly into its standard library! 

In this tutorial, we will build a robust Todo/CRM API.

## Step 1: Initialize the Database

Use the native `db_open` and `db_execute` commands to create a local SQLite database effortlessly.

```epl
Display "Initializing Database..."

db = db_open("tasks.db")
db_execute(db, "CREATE TABLE IF NOT EXISTS todos (id INTEGER PRIMARY KEY, task TEXT, done INTEGER)")
```

## Step 2: Seed the Database

EPL allows you to insert data dynamically.

```epl
existing = db_query(db, "SELECT count(*) as count FROM todos")
If existing.count == 0 Then
    db_execute(db, "INSERT INTO todos (task, done) VALUES ('Master EPL', 1)")
End
```

## Step 3: Hook it up to the Web

Now we connect our backend data to a JSON endpoint. Notice how cleanly `db_query` automatically turns database records into JSON-serializable Maps!

```epl
Create WebApp called todoAPI

Route "/api/todos" responds with
    records = db_query(db, "SELECT * FROM todos")
    Send json records
End

Start todoAPI on port 3001
```

## Production Considerations

When deploying this, remember that SQLite databases are local to the container instance running them. Choose persistent volumes on your host (like Render Disks or Railway Volumes) if you wish to persist the database between redeploys!
