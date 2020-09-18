#CREATE STATEMENTS


#DIMENSION TABLES

date_dimension_create = """
	CREATE TABLE dimDate
	(
	  date_key int primary key,
	  date date not null,
	  year smallint not null,
	  quarter smallint not null,
	  month smallint not null,
	  day smallint not null,
	  week smallint not null,
	  is_weekend boolean not null
	);
"""


customer_dimension_create = """
	CREATE TABLE dimCustomer
	(
	  customer_key SERIAL PRIMARY KEY,
	  customer_id  smallint NOT NULL,
	  first_name   varchar(45) NOT NULL,
	  last_name    varchar(45) NOT NULL,
	  email        varchar(50),
	  address      varchar(50) NOT NULL,
	  address2     varchar(50),
	  district     varchar(20) NOT NULL,
	  city         varchar(50) NOT NULL,
	  country      varchar(50) NOT NULL,
	  postal_code  varchar(10),
	  phone        varchar(20) NOT NULL,
	  active       smallint NOT NULL,
	  create_date  timestamp NOT NULL,
	  start_date   date NOT NULL,
	  end_date     date NOT NULL
	);
"""


movie_dimension_create = """
	CREATE TABLE dimMovie
	(
	  movie_key          SERIAL PRIMARY KEY,
	  film_id            smallint NOT NULL,
	  title              varchar(255) NOT NULL,
	  description        text,
	  release_year       year,
	  language           varchar(20) NOT NULL,
	  original_language  varchar(20),
	  rental_duration    smallint NOT NULL,
	  length             smallint NOT NULL,
	  rating             varchar(5) NOT NULL,
	  special_features   varchar(60) NOT NULL
	);
"""


store_dimension_create = """
	CREATE TABLE dimStore
	(
	  store_key           SERIAL PRIMARY KEY,
	  store_id            smallint NOT NULL,
	  address             varchar(50) NOT NULL,
	  address2            varchar(50),
	  district            varchar(20) NOT NULL,
	  city                varchar(50) NOT NULL,
	  country             varchar(50) NOT NULL,
	  postal_code         varchar(10),
	  manager_first_name  varchar(45) NOT NULL,
	  manager_last_name   varchar(45) NOT NULL,
	  start_date          date NOT NULL,
	  end_date            date NOT NULL
	);
"""


#FACTS TABLE

sales_fact_create = """
	CREATE TABLE factSales
	(
	    sales_key Serial primary key,
	    date_key int not null references dimDate (date_key), 
	    customer_key int not null references dimCustomer (customer_key),
	    movie_key int not null references dimMovie (movie_key),
	    store_key int not null references dimStore (store_key),
	    sales_amount numeric not null
	);
"""


#DROP STATEMENTS 


drop_date_dimension= """

	DROP IF EXISTS TABLE dimDate;

"""

drop_customer_dimension= """

	DROP IF EXISTS TABLE dimCustomer;

"""

drop_movie_dimension = """

	DROP IF EXISTS TABLE dimMovie;

"""

drop_store_dimension = """

	DROP IF EXISTS TABLE dimStore;

"""


drop_sales_fact = """

	DROP IF EXISTS TABLE factSales;

"""


#INSERT STATEMENTS

insert_date_dimension = """

	INSERT INTO dimDate (date_key, date, year, quarter, month, day, week, is_weekend)
	SELECT DISTINCT(TO_CHAR(payment_date :: DATE, 'yyyyMMDD')::integer) AS date_key,
	       date(payment_date)                                           AS date,
	       EXTRACT(year FROM payment_date)                              AS year,
	       EXTRACT(quarter FROM payment_date)                           AS quarter,
	       EXTRACT(month FROM payment_date)                             AS month,
	       EXTRACT(day FROM payment_date)                               AS day,
	       EXTRACT(week FROM payment_date)                              AS week,
	       CASE WHEN EXTRACT(ISODOW FROM payment_date) IN (6, 7) THEN true ELSE false END AS is_weekend
	FROM payment;
	
"""

insert_customer_dimension= """

	INSERT INTO dimCustomer (customer_key, customer_id, first_name, last_name, email, address, 
	                         address2, district, city, country, postal_code, phone, active, 
	                         create_date, start_date, end_date)
	SELECT 
	       c.customer_id As customer_key,
	       c.customer_id As customer_id,
	       c.first_name As first_name,
	       c.last_name As last_name,
	       c.email As email,
	       a.address As address,
	       a.address2 As address2,
	       a.district As district,
	       ci.city As city,
	       co.country As country,
	       a.postal_code As postal_code,
	       a.phone As phone,
	       c.active As active,
	       c.create_date As create_date,
	       now()         AS start_date,
	       now()         AS end_date
	FROM customer c
	JOIN address a  ON (c.address_id = a.address_id)
	JOIN city ci    ON (a.city_id = ci.city_id)
	JOIN country co ON (ci.country_id = co.country_id);

"""

insert_movie_dimension = """

	INSERT INTO dimMovie (movie_key, film_id, title, description, release_year,
	                     language, original_language, rental_duration, length,
	                     rating, special_features)
	SELECT 
	        f.film_id As movie_key,
	        f.film_id As film_id,
	        f.title As title,
	        f.description As description,
	        f.release_year As release_year,
	        l.name As language,
	        orig_lang.name AS original_language,
	        f.rental_duration As rental_duration,
	        f.length As length,
	        f.rating As rating,
	        f.special_features As special_features
	FROM film f
	JOIN language l              ON (f.language_id=l.language_id)
	LEFT JOIN language orig_lang ON (f.original_language_id = orig_lang.language_id);

"""

insert_store_dimension = """

	INSERT INTO dimStore(store_key, store_id, address, address2, district, city,
	                    country, postal_code, manager_first_name, manager_last_name, 
	                    start_date, end_date)
	SELECT
	    s.store_id As store_key,
	    s.store_id As store_id,
	    a.address As address,
	    a.address2 As address2,
	    a.district As district,
	    ci.city As city,
	    co.country As country,
	    a.postal_code As postal_code,
	    st.first_name As manager_first_name,
	    st.last_name As manager_last_name,
	    now() AS start_date,
	    now() AS end_date
	FROM store s
	JOIN address a on (s.address_id = a.address_id)
	JOIN city ci on (ci.city_id = a.city_id)
	JOIN country co on (co.country_id = ci.country_id)
	JOIN staff st on (st.staff_id = s.manager_staff_id);

"""

insert_sales_fact = """

	INSERT INTO factSales (date_key, customer_key, movie_key, store_key, sales_amount)

	SELECT
	    DISTINCT(TO_CHAR(p.payment_date :: DATE, 'yyyyMMDD')::integer) As date_key,
	    p.customer_id As customer_key,
	    i.film_id As movie_key,
	    i.store_id As store_key,
	    p.amount As sales_amount
	FROM payment p
	JOIN rental r on (r.rental_id = p.rental_id)
	JOIN inventory i on (i.inventory_id = r.inventory_id);

"""



