<?php

return [
    /*
     * The recognition client must send a similarity score between 0 and 1.
     * Tune this after measuring false matches with the camera used at the
     * cashier desk; a higher value is stricter.
     */
    // FaceNet512 cosine similarity. This matches the local client threshold
    // of cosine distance <= 0.40 (similarity >= 0.60).
    'minimum_score' => (float) env('FACE_MATCH_MIN_SCORE', 0.60),

    // A detection is only available to a cashier for this many seconds.
    'detection_ttl_seconds' => (int) env('FACE_DETECTION_TTL_SECONDS', 30),

    // Keep enabled in production. Set false only while migrating a legacy AI client.
    'require_liveness' => filter_var(env('FACE_REQUIRE_LIVENESS', true), FILTER_VALIDATE_BOOL),
];
