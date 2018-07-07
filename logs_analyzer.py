#!/usr/bin/env python3

import psycopg2
import datetime


def QueryPopularArticles(cursor):
    # Query: What are the most popular three articles of all time?
    new_view = '''
        create or replace view slug_views as
        select substring (path, 10) as slug, count(*)
        from log
        where path != '/' and status = '200 OK'
        group by slug;
        '''
    cursor.execute(new_view)
    query = '''
        select title, count
        from articles, slug_views
        where articles.slug = slug_views.slug
        order by count desc
        limit 3;
        '''
    cursor.execute(query)
    rows = cursor.fetchall()

    # Display the results
    print('\nThese are the three most popular articles in the website:\n')
    for item in rows:
        print('\"' + item[0] + '\"' + ' - ' + str(item[1]) + ' views')


def QueryPopularAuthors(cursor):
    # Query: Who are the most popular article authors of all time?
    # Use view created from the previous query
    query = '''
        select authors.name, sum(slug_views.count) as author_views
        from authors, articles, slug_views
        where authors.id = articles.author and articles.slug = slug_views.slug
        group by authors.name
        order by author_views desc;
        '''
    cursor.execute(query)
    rows = cursor.fetchall()

    # Display the results
    print('\nHere are the article authors sorted by popularity:\n')
    for item in rows:
        print(item[0] + ' - ' + str(item[1]) + ' views')


def QueryBadDays(cursor):
    # Query: On which days did more than 1% of requests lead to errors?
    requests_view = '''
        create or replace view requests
        as select time::date, count(*) as num_requests
        from log
        group by time::date;
        '''
    cursor.execute(requests_view)
    errors_view = '''
        create or replace view errors
        as select time::date, count(*) as num_error
        from log
        where status != '200 OK'
        group by time::date;
        '''
    cursor.execute(errors_view)
    query = '''
        select time, error_percentage
        from (select requests.time, num_error::float/num_requests
            as error_percentage
            from requests, errors
            where requests.time = errors.time) as error_per_day
        where error_percentage > 0.01;
        '''
    cursor.execute(query)
    rows = cursor.fetchall()

    # Display the results
    print('\nOn these days, more than 1% of page requests led to an error:\n')
    for item in rows:
        date_string = item[0].strftime("%B %d, %Y")
        print(date_string + ' - ' + "{0:.1%}".format(item[1]) + ' errors')


if __name__ == '__main__':
    # Set-up the database connection
    db = psycopg2.connect("dbname=news")
    cursor = db.cursor()

    print("\nLOG SUMMARY")

    # Analyse the log and display results
    QueryPopularArticles(cursor)
    QueryPopularAuthors(cursor)
    QueryBadDays(cursor)

    print("\n")

    # Close database connection
    db.close()
