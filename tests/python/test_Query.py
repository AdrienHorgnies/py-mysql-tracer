import query


def test_query_str():
    tested_query = query.Query('tests/assets/sample-query.sql')

    assert tested_query.query_str == "SELECT name, title FROM person LEFT JOIN job " \
                                     "ON person.job_id = job.id WHERE title NOT IN ('developer');"
