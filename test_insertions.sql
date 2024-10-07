INSERT INTO category (id, nota_id, description) VALUES (1, '55', 'Bebidas');
INSERT INTO category (id, nota_id, description) VALUES (2, '57', 'Alimentos');

INSERT INTO local (id, geohash, name) VALUES (1, 'ezs42', 'Local A');
INSERT INTO local (id, geohash, name) VALUES (2, 'ezs43', 'Local B');
INSERT INTO local (id, geohash, name) VALUES (3, 'ezs44', 'Local C');

INSERT INTO query (id, term, radius, category_id) VALUES (1, 'refri 2l', 5.0, 1);
INSERT INTO query (id, term, radius, category_id) VALUES (2, 'refri lata', 10.0, 2);

INSERT INTO query_local (query_id, local_id) VALUES (1, 1);
INSERT INTO query_local (query_id, local_id) VALUES (1, 2);
INSERT INTO query_local (query_id, local_id) VALUES (2, 3);

INSERT INTO spreadsheet (id, google_id, query_id, is_populated, last_populated) VALUES (1, 'google-id-123', 1, 1, '22-11-2024');
INSERT INTO spreadsheet (id, google_id, query_id, is_populated) VALUES (2, 'google-id-456', 2, 0);

