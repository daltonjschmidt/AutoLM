-- View: public.vw_players

-- DROP VIEW public.vw_players;

CREATE OR REPLACE VIEW public.vw_players
 AS
 SELECT p.gsis_id,
    p.team,
    p.birth_state,
    p.pandascore_id,
    p.injury_status,
    p.swish_id,
    p.yahoo_id,
    p.height,
    p.full_name,
    p.sportradar_id,
    p.years_exp,
    p."position",
    p.espn_id,
    p.practice_participation,
    p.depth_chart_order,
    p.injury_notes,
    p.birth_country,
    p.birth_city,
    p.search_rank,
    p.hashtag,
    p.birth_date,
    p.injury_body_part,
    p.high_school,
    p.weight,
    p.search_first_name,
    p.competitions,
    p.injury_start_date,
    p.practice_description,
    p.sport,
    p.rotowire_id,
    p.status,
    p.number,
    p.metadata,
    p.college,
    p.opta_id,
    p.player_id,
    p.stats_id,
    p.search_full_name,
    p.news_updated,
    p.active,
    p.depth_chart_position,
    p.last_name,
    p.fantasy_data_id,
    p.oddsjam_id,
    p.search_last_name,
    p.first_name,
    p.fantasy_positions,
    p.age,
    p.rotoworld_id,
        CASE
            WHEN d.player_id IS NOT NULL THEN 1
            ELSE 0
        END AS was_drafted
   FROM players p
     LEFT JOIN drafts d ON p.player_id = d.player_id;

ALTER TABLE public.vw_players
    OWNER TO postgres;

