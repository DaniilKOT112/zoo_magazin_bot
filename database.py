import psycopg2

db = {
    'dbname': 'db_psql_dan',
    'user': 'db_psql_dan_usr',
    'password': 'fYZvfxMr6Xg9f3tL',
    'host': '5.183.188.132',
    'port': '5432'
}
create_table_query = """
CREATE TABLE IF NOT EXISTS public.categories
(
    id_categories integer NOT NULL DEFAULT nextval('categories_id_categories_seq'::regclass),
    name_categories text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT categories_pkey PRIMARY KEY (id_categories),
    CONSTRAINT unique_name_categories UNIQUE (name_categories)
);

CREATE TABLE IF NOT EXISTS public.parent_category
(
    id_parent_category integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT parent_category_pkey PRIMARY KEY (id_parent_category),
    CONSTRAINT unique_id UNIQUE (id_parent_category),
    CONSTRAINT unique_name UNIQUE (name)
);
  
CREATE TABLE IF NOT EXISTS public.categories_parent_category
(
    id_categories_parent_category integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    id_categories integer NOT NULL,
    id_parent_categories integer NOT NULL,
    CONSTRAINT categories_parent_category_pkey PRIMARY KEY (id_categories_parent_category),
    CONSTRAINT id_cetegories FOREIGN KEY (id_categories)
        REFERENCES public.categories (id_categories) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT id_parent_category FOREIGN KEY (id_parent_categories)
        REFERENCES public.parent_category (id_parent_category) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
 
CREATE TABLE IF NOT EXISTS public.product
(
    id_product integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name text COLLATE pg_catalog."default" NOT NULL,
    id_image integer NOT NULL,
    id_category integer NOT NULL,
    description text COLLATE pg_catalog."default" NOT NULL,
    amount bigint NOT NULL DEFAULT nextval('product_amount_seq'::regclass),
    price money NOT NULL,
    CONSTRAINT product_pkey PRIMARY KEY (id_product),
    CONSTRAINT categories_parent_categories FOREIGN KEY (id_category)
        REFERENCES public.categories_parent_category (id_categories_parent_category) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT image FOREIGN KEY (id_image)
        REFERENCES public.image (id_image) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS public.image
(
    id_image integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    url bytea,
    CONSTRAINT image_pkey PRIMARY KEY (id_image)
);

CREATE TABLE IF NOT EXISTS public."order"
(
    id_order integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    order_date date NOT NULL,
    CONSTRAINT order_pkey PRIMARY KEY (id_order)
);

CREATE TABLE IF NOT EXISTS public.order_details
(
    id_product_order integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    id_product integer NOT NULL,
    id_order integer NOT NULL,
    amount integer NOT NULL,
    price money NOT NULL,
    CONSTRAINT product_order_pkey PRIMARY KEY (id_product_order),
    CONSTRAINT "order" FOREIGN KEY (id_order)
        REFERENCES public."order" (id_order) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID,
    CONSTRAINT product FOREIGN KEY (id_product)
        REFERENCES public.product (id_product) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
        NOT VALID
);
"""

connection = psycopg2.connect(**db)
cursor = connection.cursor()
cursor.execute(create_table_query)
connection.commit()
