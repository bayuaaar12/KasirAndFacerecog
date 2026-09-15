<?php

namespace Tests\Feature;

use Tests\TestCase;

class FaceApiSecurityTest extends TestCase
{
    public function test_face_detection_requires_an_api_key(): void
    {
        $response = $this->postJson('/api/customers/detect-member', [
            'face_label' => 'any_member',
            'score' => 0.99,
            'liveness_passed' => true,
        ]);

        $response->assertUnauthorized();
    }
}
