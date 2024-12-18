-- View: public.vw_running_wins

-- DROP VIEW public.vw_running_wins;

CREATE OR REPLACE VIEW public.vw_running_wins
 AS
 SELECT year_week_matchup,
    year,
    week_number,
    roster_year,
    total_points,
    win_flag,
    sum(win_flag) OVER (PARTITION BY roster_year ORDER BY week_number) AS running_total_win_flag
   FROM ( SELECT p.year_week_matchup,
            p.year,
            p.week_number,
            p.roster_year,
            sum(p.player_points::numeric) AS total_points,
                CASE
                    WHEN p.roster_year = w.winner THEN 1
                    ELSE 0
                END AS win_flag
           FROM player_performances p
             LEFT JOIN vw_weekly_summaries w ON p.year_week_matchup = w.year_week_matchup
          WHERE p.starter::text = 'true'::text
          GROUP BY p.year_week_matchup, p.year, p.week_number, p.roster_year, (
                CASE
                    WHEN p.roster_year = w.winner THEN 1
                    ELSE 0
                END)) subquery_alias
  ORDER BY year DESC, week_number;

ALTER TABLE public.vw_running_wins
    OWNER TO postgres;

