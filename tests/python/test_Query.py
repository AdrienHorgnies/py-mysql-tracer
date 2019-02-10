import mysql_tracer


def test_query_str():
    tested_query = mysql_tracer.Query('tests/assets/sample-query.sql')

    assert tested_query.query_str == "SELECT name, title FROM person LEFT JOIN job " \
                                     "ON person.job_id = job.id WHERE title NOT IN ('developer');"
