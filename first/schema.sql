drop table if exists Tweets;
create table Tweets (
  Data_id integer primary key autoincrement,
  Tweet_ID integer,
  Text varchar,
  GeoX decimal,
  GeoY decimal
);

