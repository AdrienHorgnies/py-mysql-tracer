-- A first comment at the start of the file followed by a blank line

SELECT
    name, -- an inline comment exactly how I don't like them
    title

FROM person
LEFT JOIN job
    -- an indented comment followed by a badly indented equality sign
    ON person.job_id =   job.id

WHERE title NOT IN ('developer');
