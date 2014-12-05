--Filename extraschema.sql
--HELPER TABLES  
--paths2steps ... follows C_UD of paths to create 1-1 relationshitp
--steps2tags ... follows C_UD of steps to create 1-1 relationshitp
--Joseph Boakye <jboakye@bwachi.com> Oct 10 2014

DROP TABLE step2tags;
CREATE TABLE step2tags(
    id SERIAL PRIMARY KEY,
    step_id INTEGER REFERENCES steps (id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags (id) ON DELETE CASCADE,
    modified_on TIMESTAMP
);
CREATE INDEX idx_s2t_tag_id  ON step2tags(tag_id);
CREATE INDEX idx_s2t_step_id ON step2tags(step_id);

DROP TABLE path2steps;
CREATE TABLE path2steps(
    id SERIAL PRIMARY KEY,
    path_id INTEGER REFERENCES paths (id) ON DELETE CASCADE,
    step_id INTEGER REFERENCES steps (id) ON DELETE CASCADE,
    modified_on TIMESTAMP
);
CREATE INDEX idx_p2s_step_id  ON path2steps(step_id);
CREATE INDEX idx_p2s_path_id  ON path2steps(path_id);

CREATE TABLE exceptions(
    id SERIAL PRIMARY KEY,
    step TEXT,
    in_path TEXT,
    map_location TEXT,
    user_response TEXT,
    score FLOAT8,
    log_id TEXT,
    user_name INTEGER REFERENCES auth_user (id) ON DELETE CASCADE,
    date_submitted TIMESTAMP,
    bug_status INTEGER REFERENCES bug_status (id) ON DELETE CASCADE,
    admin_comment TEXT,
    hidden CHAR(1),
    uuid VARCHAR(64),
    modified_on TIMESTAMP
);

CREATE TABLE steps_inactive_locations(
    id SERIAL PRIMARY KEY,
    step_id INTEGER REFERENCES steps (id) ON DELETE CASCADE,
    loc_id INTEGER REFERENCES locations (id) ON DELETE CASCADE,
    step_desc TEXT,
    loc_desc TEXT,
    in_paths TEXT,
    modified_on TIMESTAMP
);
CREATE INDEX idx_sil_step_id  ON steps_inactive_locations(step_id);
CREATE INDEX idx_sil_loc_id  ON steps_inactive_locations(loc_id);

ALTER TABLE tag_progress
ADD COLUMN  all_cat1 INTEGER default 0,
ADD COLUMN  just_cats INTEGER default 0
;

ALTER TABLE audio
ADD COLUMN  clip_m4a  character varying(512)
;
