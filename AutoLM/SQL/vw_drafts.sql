CREATE OR REPLACE VIEW public.vw_drafts
 AS
 SELECT DISTINCT d.round,
    d.roster_id,
    d.player_id,
    d.picked_by,
    d.pick_no,
    d.draft_slot,
    d.draft_id,
    d.roster_year,
    d.year,
        CASE
            WHEN r.player_id IS NOT NULL THEN 1
            ELSE 0
        END AS on_roster,
        CASE
            WHEN r.player_id IS NOT NULL THEN 'Yes'::text
            ELSE 'No'::text
        END AS on_roster_yn
   FROM drafts d
     LEFT JOIN users u ON d.picked_by = u.user_id
     LEFT JOIN league l ON u.user_year = l.user_year
     LEFT JOIN players p ON p.player_id = d.player_id
     LEFT JOIN vw_rosters r ON d.player_id = r.player_id AND d.picked_by = r.user_id
  WHERE u.year = (( SELECT max(users.year) AS max
           FROM users));

ALTER TABLE public.vw_drafts
    OWNER TO postgres;

