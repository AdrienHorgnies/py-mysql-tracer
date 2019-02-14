-- A first comment at the start of the file followed by a blank line

SELECT
    name, -- an inline comment exactly how I don't like them
    title

FROM person
LEFT JOIN job
    -- an indented comment followed by a badly indented equality sign
    ON person.job_id =   job.id # another ugly inline comment

WHERE title NOT IN ('developer');

-- START TIME: 1992-03-04T11:00:05.654321
-- END TIME: 1992-03-04T11:00:05.987654
-- DURATION: 0:00:00.333333
-- ROWS COUNT: 2
-- RESULT FILE: 1992-03-04T11-00-05_query.csv
