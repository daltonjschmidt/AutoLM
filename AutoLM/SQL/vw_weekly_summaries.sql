-- View: public.vw_weekly_summaries

-- DROP VIEW public.vw_weekly_summaries;

CREATE OR REPLACE VIEW public.vw_weekly_summaries
 AS
 SELECT week_number,
    year,
    matchup_id,
    roster_id_1,
    roster_year_1,
    total_points_1::numeric AS total_points_1,
    roster_id_2,
    total_points_2::numeric AS total_points_2,
    year_week_matchup,
    roster_year_2,
        CASE
            WHEN year_week_matchup ~~ '%:None'::text THEN NULL::character varying::text
            WHEN total_points_1::numeric > total_points_2::numeric THEN roster_year_1
            ELSE roster_year_2
        END AS winner
   FROM weekly_summaries
  ORDER BY year DESC, week_number;

ALTER TABLE public.vw_weekly_summaries
    OWNER TO postgres;

