-- Seed 10 initial Wellness communities.
-- Run after Database_Module.create_tables() and after user_id = 1 exists.
-- The guards make this script safe to run more than once.

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Morning Flow Collective', NULL, NULL,
    'A welcoming community for energising morning yoga, mindful movement and consistent daily practice.',
    'Yoga', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Morning Flow Collective');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Stillness Circle', NULL, NULL,
    'Find quiet support through guided meditation, breathwork and simple techniques for a calmer mind.',
    'Meditation', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Stillness Circle');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'The Mindful Living Guild', NULL, NULL,
    'Practical conversations and shared routines for building a more present and intentional lifestyle.',
    'Lifestyle', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'The Mindful Living Guild');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Rooted Ayurveda Community', NULL, NULL,
    'Explore Ayurvedic-inspired habits, seasonal wellbeing and balanced living with a supportive community.',
    'Ayurveda', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Rooted Ayurveda Community');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Strong Body, Soft Mind', NULL, NULL,
    'A friendly space for sustainable fitness, recovery, mobility and the mental habits that keep us going.',
    'Fitness', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Strong Body, Soft Mind');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'The Inner Compass', NULL, NULL,
    'Reflect, learn and connect through thoughtful discussions about spirituality and personal growth.',
    'Spirituality', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'The Inner Compass');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Breathe Well Network', NULL, NULL,
    'Peer support for stress management, mindful breathing and small practices that improve mental wellness.',
    'Mental Wellness', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Breathe Well Network');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Sunrise Yoga Studio', NULL, NULL,
    'Build strength, flexibility and connection with accessible yoga sessions for every experience level.',
    'Yoga', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Sunrise Yoga Studio');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Quiet Minds Fellowship', NULL, NULL,
    'A respectful private community for deeper meditation practice, reflection and weekly check-ins.',
    'Meditation', 'private', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Quiet Minds Fellowship');

INSERT INTO organizations
    (name, logo_url, cover_image_url, description, category, privacy, created_by)
SELECT
    'Wellness Makers Hub', NULL, NULL,
    'Share realistic wellbeing goals, useful resources and encouragement while creating healthier routines.',
    'Lifestyle', 'public', 1
FROM users
WHERE user_id = 1
  AND NOT EXISTS (SELECT 1 FROM organizations WHERE name = 'Wellness Makers Hub');

COMMIT;
