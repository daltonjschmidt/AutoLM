-- View: public.vw_league

-- DROP VIEW public.vw_league;

CREATE OR REPLACE VIEW public.vw_league
 AS
 SELECT l.roster_id,
    l.owner_id,
    l.streak,
    l.record,
    l.wins,
    l.losses,
    l.ties,
    l.possible_points_for,
    l.actual_points_for,
    l.points_against,
    l.division,
    l.moves,
    l.year,
    l.user_year,
    l.roster_year,
    round(l.wins::numeric / (l.wins + l.losses + l.ties)::numeric, 2) AS win_perc,
        CASE
            WHEN p.is_champion::text = 'true'::text THEN 1
            ELSE 0
        END AS championships,
    u.display_name,
    rw.running_total_win_flag AS total_wins
   FROM league l
     LEFT JOIN playoffs p ON l.roster_year = p.roster_year
     LEFT JOIN users u ON u.user_id = l.owner_id AND u.year::text = l.year::text
     LEFT JOIN vw_running_wins rw ON l.roster_year = rw.roster_year
  WHERE rw.year < 2022 AND rw.week_number = 17 OR rw.year >= 2022 AND rw.week_number = 18;

ALTER TABLE public.vw_league
    OWNER TO postgres;

