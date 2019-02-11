-- A first comment at the start of the file followed by a blank line

SELECT
    '{', -- trying to trap template engine here
    '$jobs}', -- trying to trap template engine in a very mean way
    name, -- an inline comment exactly how I don't like them
    title

FROM person
LEFT JOIN job
    -- an indented comment followed by a badly indented equality sign
    ON person.job_id =   job.id # another ugly inline comment

WHERE title $disappear IN ('${job}');
