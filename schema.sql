SELECT * FROM auth_logs LIMIT 24;

SELECT * FROM auth_logs WHERE login_result = 'failure';

--SELECT * FROM auth_logs LIMIT 1;

SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'auth_logs';

--SELECT * FROM auth_logs WHERE login_result = 'failure';

SELECT username, COUNT(*) AS total_attempts
FROM auth_logs
GROUP BY username
ORDER BY total_attempts DESC;


SELECT ip_address,
       COUNT(*) AS failed_attempts,
       MIN(timestamp) AS first_attempt,
       MAX(timestamp) AS last_attempt
FROM auth_logs
WHERE login_result = 'FAILED'
GROUP BY ip_address, DATE_TRUNC('minute', timestamp)
HAVING COUNT(*) >= 5
ORDER BY failed_attempts DESC;


SELECT column_name
FROM information_schema.columns
WHERE table_name = 'auth_logs';


SELECT login_result, COUNT(*)
FROM auth_logs
GROUP BY login_result;

