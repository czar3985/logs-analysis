# Log Analyzer

A program that runs from the command line that connects to the database, sends 
SQL queries and provides a report. The database is from a newspaper site. It contains
information about articles, authors and logs from user visits to the website.


## Prerequisites

1. **python 3.6.3**
2. _psycopg2_ library
3. **PostgreSQL**
4. _logs_analyzer.py_ from the github repository [logs-analysis](https://github.com/czar3985/logs-analysis).

## Usage

Run the python script _logs_analyzer.py_. The report will be displayed on the command line interface.

## About the program

The database _newsdata.sql_ consists of three tables: Authors, Articles and Log. 
The structures of each table are as follows:

**Authors**
```
 Column |  Type   |                      Modifiers
--------+---------+------------------------------------------------------
 name   | text    | not null
 bio    | text    |
 id     | integer | not null default nextval('authors_id_seq'::regclass)
Indexes:
    "authors_pkey" PRIMARY KEY, btree (id)
Referenced by:
    TABLE "articles" CONSTRAINT "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)
```

**Articles**
```
 Column |           Type           |                       Modifiers            
--------+--------------------------+-------------------------------------------------------
 author | integer                  | not null
 title  | text                     | not null
 slug   | text                     | not null
 lead   | text                     |
 body   | text                     |
 time   | timestamp with time zone | default now()
 id     | integer                  | not null default nextval('articles_id_seq'::regclass)
Indexes:
    "articles_pkey" PRIMARY KEY, btree (id)
    "articles_slug_key" UNIQUE CONSTRAINT, btree (slug)
Foreign-key constraints:
    "articles_author_fkey" FOREIGN KEY (author) REFERENCES authors(id)
```

**Log**
```
 Column |           Type           |                    Modifiers               
--------+--------------------------+--------------------------------------------------
 path   | text                     |
 ip     | inet                     |
 method | text                     |
 status | text                     |
 time   | timestamp with time zone | default now()
 id     | integer                  | not null default nextval('log_id_seq'::regclass)
Indexes:
    "log_pkey" PRIMARY KEY, btree (id)
```

### The Reporting Tool

The tool provides the answers to these questions:
1. What are the most popular three articles of all time?
2. Who are the most popular article authors of all time?
3. On which days did more than 1% of requests lead to errors?

**Views**

All views are created and replaced inside the logs analyzer code.

The first and second queries make use of the ```slug_views``` view:
```sql
create or replace view slug_views as
select substring (path, 10) as slug, count(*)
from log
where path != '/' and status = '200 OK'
group by slug;
``` 
The table saved in ```slug_views``` from the statement above: 
- gets the article keyword from the request path using ```substring```, and
- counts the successful views for each article.

The third query makes use of the ```requests``` and ```errors``` views:
```sql
create or replace view requests
as select time::date, count(*) as num_requests
from log
group by time::date;

create or replace view errors
as select time::date, count(*) as num_error
from log
where status != '200 OK'
group by time::date;
```

```requests``` view shows the total requests received by the website daily.

```errors``` view shows the total requests received by the website daily that
resulted in an error. If HTTP status is not 200, the request resulted in an error.

**Top 3 Popular Articles**
- Slug_views table is joined to Articles table in order
to produce the Article titles and the corresponding user visit for each.
- The result is sorted based on number of user visits.
- The top 3 articles are displayed.

**Authors Listed By Popularity**
- With joins, the author for each article with corresponding
number of user visits is determined.
- The sum of user visits per author is computed.
- The authors are listed based on their popularity.

**Days When There Were High Error Rates**
- Only the status and time columns from the log table are used.
- The date is extracted from the time column entries with ```time::date```.
- Per day, the error rate is computed using the values from total requests received
per day and errors encountered per day.
- ```::float``` is used for higher precision when performing the division operation.
- The date was formatted with the ```strftime``` method and the error rate formatted
to display a percentage.

## Output
```
LOG SUMMARY

These are the three most popular articles in the website:

"Candidate is jerk, alleges rival" - 338647 views
"Bears love berries, alleges bear" - 253801 views
"Bad things gone, say good people" - 170098 views

Here are the article authors sorted by popularity:

Ursula La Multa - 507594 views
Rudolf von Treppenwitz - 423457 views
Anonymous Contributor - 170098 views
Markoff Chaney - 84557 views

On these days, more than 1% of page requests led to an error:

July 17, 2016 - 2.3% errors
```

## License

Log Analyzer is released under the [MIT License](https://opensource.org/licenses/MIT).