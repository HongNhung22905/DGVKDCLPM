-- Migration: make AiSession.userId nullable to support guest rate-limiting
-- AiSession rows from guests will have userId = NULL; FK cascade only fires for real users.

ALTER TABLE "AiSession" ALTER COLUMN "userId" DROP NOT NULL;
