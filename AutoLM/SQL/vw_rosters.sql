-- View: public.vw_rosters

-- DROP VIEW public.vw_rosters;

CREATE OR REPLACE VIEW public.vw_rosters
 AS
 SELECT r.year,
    r.roster_id,
    r.player_id,
    r.roster_year,
    r.year_roster_player,
    u.user_id
   FROM rosters r
     LEFT JOIN league l ON r.roster_year = l.roster_year
     LEFT JOIN users u ON l.user_year = u.user_year;

ALTER TABLE public.vw_rosters
    OWNER TO postgres;

