

to make it work you need to add to the oidc table in the db.

list clients:
```sql
select * from oidc where type = 'clients';
```

add client

```sql
INSERT INTO oidc (`type`, `key`, `value`, `last_modified`)
VALUES (
  'clients',
  'CLIENT_ID',
  '{"redirect_uri": "REDIRECT_URL", "client_secret": "CLIENT_SECRET"}',
  CURRENT_TIMESTAMP
);
```

Some systems may require an `token_endpoint_auth_method` in the value
- outline needs `client_secret_post`

callback:
- outline uses `/auth/oidc.callback`