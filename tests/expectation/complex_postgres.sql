CREATE SCHEMA IF NOT EXISTS "another";

CREATE SCHEMA IF NOT EXISTS "example";

CREATE TYPE example.answer AS ENUM ('n/a','yes','no');

CREATE TABLE "another"."user" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "name" VARCHAR(255) UNIQUE,
  "value" DECIMAL(12, 4) CHECK (value > 0),
  CONSTRAINT chk_name_length CHECK (LENGTH("name") <= 255)
);

CREATE UNIQUE INDEX "idx_user_name" ON "another"."user"("name");

CREATE TABLE "example"."option" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "seq" INT,
  "content" VARCHAR(255)
);

CREATE INDEX "idx_option_seq" ON "example"."option"("seq");

CREATE UNIQUE INDEX "idx_option_seq_content" ON "example"."option"("seq", "content");

CREATE TABLE "example"."question" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "content" VARCHAR(255),
  "option_id" INT,
  CONSTRAINT fk_question_option FOREIGN KEY ("option_id") REFERENCES "example"."option" (
    "id"
  ) ON UPDATE NO ACTION
);

CREATE INDEX "idx_question_content" ON "example"."question"("content");

CREATE TABLE "example"."questionare" (
  "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  "name" VARCHAR(255),
  "question_id" INT,
  CONSTRAINT fk_questionare_question FOREIGN KEY ("question_id") REFERENCES "example"."question" (
    "id"
  ) ON DELETE CASCADE
);

CREATE INDEX "idx_questionare_name" ON "example"."questionare"("name");

CREATE TABLE "example"."user_survey" (
  "id" INT GENERATED ALWAYS AS IDENTITY,
  "user_id" INT REFERENCES "another"."user" (
    "id"
  ),
  "questionare_id" INT,
  "submission_date" TIMESTAMP DEFAULT now(),
  "answer_given" example.answer NOT NULL,
  CONSTRAINT fk_user_survey_questionare FOREIGN KEY ("questionare_id") REFERENCES "example"."questionare" (
    "id"
  ),
  PRIMARY KEY ("user_id", "questionare_id")
);

CREATE INDEX "idx_user_survey_submission_date" ON "example"."user_survey"("submission_date");

CREATE INDEX "idx_user_survey_answer_given" ON "example"."user_survey"("answer_given");

