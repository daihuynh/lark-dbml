CREATE TABLE "orders" (
    "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "status" VARCHAR(50) NULL DEFAULT 'new',
    "total" DECIMAL(10, 2) NULL DEFAULT 0,
    "is_paid" BOOLEAN NULL DEFAULT false,
    "notes" TEXT,
    "updated_at" TIMESTAMP
);

CREATE TABLE "items" (
    "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "order_id" INT NULL REFERENCES "orders" ("id"),
    "product_name" VARCHAR(255) NOT NULL,
    "quantity" INT NULL DEFAULT 1 CHECK (quantity > 0),
    "price" DECIMAL(10, 2)
);

CREATE TABLE "user_logs" (
    "log_id" UUID NULL DEFAULT gen_random_uuid(),
    "action" TEXT,
    "timestamp" TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
);
