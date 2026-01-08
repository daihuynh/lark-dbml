CREATE TABLE "users" (
    "id" INT PRIMARY KEY,
    "email" VARCHAR(255),
    "username" VARCHAR(50),
    "bio" TEXT
);

CREATE UNIQUE INDEX "idx_users_email" ON "users" ("email");
CREATE INDEX "idx_users_naming" ON "users" ("username","email");
CREATE INDEX "idx_bio_partial" ON "users" ("bio");
