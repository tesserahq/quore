Given pool_size=20 and max_overflow=30, *one process* can legitimately open up to 50 PostgreSQL connections for quore-api. 


Factor in number of workers
If you run, say, 4 app workers, the theoretical max is:
4 * (pool_size + max_overflow) = 4 * 50 = 200 connections.
Make sure your Postgres max_connections can handle that plus admin tools, migrations, etc.

SHOW max_connections: 100





```SELECT id, metadata_ FROM public.data_4ceb74e2_653d_4d82_9be2_e90e983ab535_index
ORDER BY id ASC 


delete from public.data_4ceb74e2_653d_4d82_9be2_e90e983ab535_index;


SELECT 
    pid
    ,datname
    ,usename
    ,application_name
    ,client_hostname
    ,client_port
    ,backend_start
    ,query_start
    ,query
    ,state
FROM pg_stat_activity
order by application_name


SHOW max_connections;
```