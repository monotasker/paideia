CREATE TABLE attempt_log (
    "id" serial PRIMARY KEY,
    "name" INTEGER,
    "score" DOUBLE,
    "dt_attempted" TIMESTAMP,
    "step" INTEGER,
    "in_path" INTEGER,
    "user_response" CHAR(512)
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE audio(
    id serial PRIMARY KEY,
    clip CHAR(512),
    title CHAR(512),
    description CHAR(512)
, clip_ogg CHAR(128), uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE auth_cas(
    id serial PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    created_on TIMESTAMP,
    url CHAR(512),
    uuid CHAR(512)
, service CHAR(512), renew CHAR(1), ticket CHAR(512), modified_on TIMESTAMP);
CREATE TABLE auth_event(
    id serial PRIMARY KEY,
    time_stamp TIMESTAMP,
    client_ip CHAR(512),
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    origin CHAR(512),
    description TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE auth_group(
    id serial PRIMARY KEY,
    role CHAR(512),
    description TEXT
, paths_per_day INTEGER, end_date TIMESTAMP, term CHAR(512), start_date TIMESTAMP, course_section CHAR(512), academic_year INTEGER, course_instructor INTEGER REFERENCES auth_user (id) ON DELETE CASCADE, institution CHAR(512), days_per_week INTEGER, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE auth_membership(
    id serial PRIMARY KEY,
    user_id INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    group_id INTEGER REFERENCES auth_group(id) ON DELETE CASCADE
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE auth_permission(
    id serial PRIMARY KEY,
    group_id INTEGER REFERENCES auth_group(id) ON DELETE CASCADE,
    name CHAR(512),
    table_name CHAR(512),
    record_id INTEGER
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE auth_user(
    id serial PRIMARY KEY,
    first_name CHAR(128),
    last_name CHAR(128),
    email CHAR(512),
    password CHAR(512),
    registration_key CHAR(512),
    reset_password_key CHAR(512)
, registration_id CHAR(512), time_zone TEXT, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE badges(
    id serial PRIMARY KEY,
    badge_name CHAR(512) UNIQUE,
    tag INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    description TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE badges_begun(
    id serial PRIMARY KEY,
    name INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    tag INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    cat1 TIMESTAMP,
    cat2 TIMESTAMP,
    cat3 TIMESTAMP,
    cat4 TIMESTAMP
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE bug_status (
    "id" serial PRIMARY KEY,
    "status_label" TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE bugs (
    "id" serial PRIMARY KEY,
    "step" INTEGER,
    "user_response" CHAR(512),
    "user_name" INTEGER,
    "date_submitted" TIMESTAMP,
    "bug_status" INTEGER,
    "admin_comment" TEXT,
    "prev_lastright" TIMESTAMP,
    "prev_lastwrong" TIMESTAMP,
    "log_id" INTEGER,
    "score" INTEGER,
    "hidden" CHAR(1),
    "map_location" INTEGER,
    "in_path" INTEGER
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE categories(
    id serial PRIMARY KEY,
    category CHAR(512),
    description CHAR(512)
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE classes(
    id serial PRIMARY KEY,
    institution CHAR(512) UNIQUE,
    academic_year INTEGER,
    term CHAR(512),
    course_section CHAR(512),
    instructor INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    paths_per_day INTEGER,
    days_per_week INTEGER,
    members TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE constructions(
    id serial PRIMARY KEY,
    construction_label CHAR(512) UNIQUE,
    readable_label CHAR(512) UNIQUE,
    trans_regex_eng CHAR(512),
    trans_templates TEXT,
    form_function CHAR(512),
    instructions TEXT,
    tags TEXT
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE content_pages(
    id serial PRIMARY KEY,
    content TEXT,
    first_authored TIMESTAMP,
    last_updated TIMESTAMP,
    author INTEGER REFERENCES auth_user (id) ON DELETE CASCADE
, title CHAR(512), topics INTEGER REFERENCES topics (id) ON DELETE CASCADE, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE images(
    id serial PRIMARY KEY,
    image CHAR(512),
    title CHAR(512),
    description CHAR(512)
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE inv_items(
    id serial PRIMARY KEY,
    item_name CHAR(512)
, item_image INTEGER REFERENCES images(id) ON DELETE CASCADE);
CREATE TABLE inventory(
    id serial PRIMARY KEY,
    owner INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    items_held TEXT
);
CREATE TABLE journal_pages(
    id serial PRIMARY KEY,
    journal_page TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE journals (
    "id" serial PRIMARY KEY,
    "pages" TEXT,
    "name" INTEGER,
    "journal_pages" TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE lemmas(
    id serial PRIMARY KEY,
    lemma CHAR(512),
    part_of_speech CHAR(512),
    glosses TEXT,
    first_tag INTEGER REFERENCES tags (id) ON DELETE CASCADE,
    extra_tags TEXT
, uuid CHAR(64), thematic_pattern CHAR(512), real_stem CHAR(512), modified_on TIMESTAMP);
CREATE TABLE locations (
    "id" serial PRIMARY KEY,
    "location" CHAR(512),
    "alias" CHAR(512),
    "bg_image" INTEGER,
    "readable" CHAR(512),
    "loc_alias" CHAR(512),
    "map_location" CHAR(512),
    "loc_active" CHAR(1)
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE news(
    id serial PRIMARY KEY,
    story TEXT,
    title CHAR(512),
    name INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    date_submitted TIMESTAMP,
    last_edit TIMESTAMP
);
CREATE TABLE npcs (
    "id" serial PRIMARY KEY,
    "name" CHAR(512),
    "location" TEXT,
    "notes" TEXT,
    "npc_image" INTEGER,
    "map_location" TEXT
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE path_styles(
    id serial PRIMARY KEY,
    style_label CHAR(512) UNIQUE,
    components TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE paths(
    id serial PRIMARY KEY,
    steps TEXT,
    locations TEXT,
    npcs TEXT
, label CHAR(512), tags INTEGER REFERENCES tags(id) ON DELETE CASCADE, path_style INTEGER REFERENCES path_styles (id) ON DELETE CASCADE, path_tags CHAR(512), path_active CHAR(1), uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE plugin_slider_decks (
    "id" serial PRIMARY KEY,
    "deck_name" CHAR(512),
    "deck_slides" TEXT,
    "theme" TEXT,
    "tag" TEXT,
    "deck_position" INTEGER
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE plugin_slider_slides (
    "id" serial PRIMARY KEY,
    "slide_name" CHAR(512),
    "theme" TEXT,
    "updated" TIMESTAMP,
    "slide_content" TEXT
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE plugin_slider_themes(
    id serial PRIMARY KEY,
    theme_name CHAR(512),
    description TEXT
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE session_data (
    "id" serial PRIMARY KEY,
    "updated" TIMESTAMP,
    "session_start" TIMESTAMP,
    "name" INTEGER,
    "other_data" TEXT
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE step_hints(
    id serial PRIMARY KEY,
    label CHAR(512),
    text CHAR(512)
, hint_label CHAR(512), hint_text TEXT, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE step_instructions(
    id serial PRIMARY KEY,
    label CHAR(512),
    text CHAR(512)
, instruction_text TEXT, instruction_label CHAR(512), modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE step_status(
    id serial PRIMARY KEY,
    status_num INTEGER UNIQUE,
    status_label TEXT UNIQUE
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE step_types (
    "id" serial PRIMARY KEY,
    "widget" CHAR(512),
    "step_class" CHAR(512),
    "step_type" CHAR(512)
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE steps (
    "id" serial PRIMARY KEY,
    "prompt" TEXT,
    "prompt_audio" INTEGER,
    "widget_type" INTEGER,
    "widget_image" INTEGER,
    "response1" CHAR(512),
    "readable_response" CHAR(512),
    "outcome1" CHAR(512),
    "response2" CHAR(512),
    "outcome2" CHAR(512),
    "response3" CHAR(512),
    "outcome3" CHAR(512),
    "tags" TEXT,
    "tags_secondary" TEXT,
    "npcs" TEXT,
    "status" INTEGER,
    "locations" TEXT,
    "hints" TEXT,
    "instructions" TEXT,
    "tags_ahead" TEXT,
    "step_options" TEXT,
    "lemmas" TEXT
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE tag_progress(
    id serial PRIMARY KEY,
    name INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    latest_new INTEGER REFERENCES tags(id) ON DELETE CASCADE
, cat1 TEXT, cat2 TEXT, cat3 TEXT, cat4 TEXT, rev1 TEXT, rev3 TEXT, rev2 TEXT, rev4 TEXT, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE tag_records (
    "id" serial PRIMARY KEY,
    "name" INTEGER,
    "times_right" DOUBLE,
    "times_wrong" DOUBLE,
    "tlast_wrong" TIMESTAMP,
    "tlast_right" TIMESTAMP,
    "category" INTEGER,
    "tag" INTEGER,
    "step" INTEGER,
    "secondary_right" TEXT,
    "in_path" INTEGER
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE tags (
    "id" serial PRIMARY KEY,
    "tag" CHAR(512),
    "slides" TEXT,
    "tag_position" INTEGER
, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE topics(
    id serial PRIMARY KEY,
    topic CHAR(512)
, modified_on TIMESTAMP, uuid CHAR(64));
CREATE TABLE user_stats(
    id serial PRIMARY KEY,
    name INTEGER REFERENCES auth_user (id) ON DELETE CASCADE,
    year INTEGER,
    month INTEGER,
    week INTEGER,
    updated TIMESTAMP,
    day1 TEXT,
    day2 TEXT,
    day3 TEXT,
    day4 TEXT,
    day5 TEXT,
    day6 TEXT,
    day7 TEXT,
    logs_by_tag TEXT,
    logs_right TEXT,
    logs_wrong TEXT,
    done INTEGER
, count1 TEXT, count3 TEXT, count2 TEXT, count5 TEXT, count7 TEXT, count6 TEXT, count4 TEXT, uuid CHAR(64), modified_on TIMESTAMP);
CREATE TABLE word_forms (
    "id" serial PRIMARY KEY,
    "word_form" CHAR(512),
    "source_lemma" INTEGER,
    "tense" CHAR(512),
    "voice" CHAR(512),
    "mood" CHAR(512),
    "person" CHAR(512),
    "number" CHAR(512),
    "grammatical_case" CHAR(512),
    "gender" CHAR(512),
    "construction" INTEGER,
    "tags" TEXT
, thematic_pattern CHAR(512), modified_on TIMESTAMP, declension CHAR(512), uuid CHAR(64));
CREATE INDEX idx_alog_1 ON attempt_log (name);
CREATE INDEX idx_alog_2 ON attempt_log (name, dt_attempted);
CREATE INDEX idx_alog_3 ON attempt_log (dt_attempted);
CREATE INDEX idx_badges1 ON badges (tag);
CREATE INDEX idx_bdgs_begun1 ON badges_begun (name);
CREATE INDEX idx_bdgs_begun2 ON badges_begun (tag);
CREATE INDEX idx_bugs_1 ON bugs (user_name, bug_status);
CREATE INDEX idx_tags1 ON tags (tag, tag_position);
CREATE INDEX idx_tags2 ON tags (tag_position);
CREATE INDEX idx_trecs_1 ON tag_records (name, tag);
CREATE INDEX idx_trecs_2 ON tag_records (tag, name);
CREATE INDEX idx_userstats_1 ON user_stats (week, year, name);
