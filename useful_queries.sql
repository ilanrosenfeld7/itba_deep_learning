drop table if exists "Score";
drop table if exists "Pelicula";
drop table if exists "Usuario";
drop table if exists "Trabajador";
drop table if exists "Persona";
drop table if exists "Prediction_Score";

select * from "Persona";
select * from "Usuario";
select * from "Trabajador";
select * from "Score";
select * from "Pelicula";
select * from "Prediction_Score";

select * from "Score" where user_id=1 order by pelicula_id ASC;