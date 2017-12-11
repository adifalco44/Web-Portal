drop table if exists Students;
create table Students (
  Student_id integer primary key autoincrement,
  First varchar,
  Last varchar
);

drop table if exists Classes;
create table Classes (
  Class_id integer primary key autoincrement,
  Name varchar,
  Credits integer
);

drop table if exists Schedule;
create table Schedule (
  Schedule_id integer primary key autoincrement,
  Students_id integer,
  Class_id integer
);
drop table if exists Exp;
create table Exp (
   Session_id integer primary key autoincrement,
   Image varchar,
   Opt1 varchar,
   Opt2 varchar,
   Opt3 varchar,
   Sol varchar
);
drop table if exists Data;
create table Data (
   Question_id integer primary key autoincrement,
   Correct_answer varchar,
   Submitted_answer varchar
);
