<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Customer;
use App\Models\MemberDetection;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

// [AI/ML INTEGRATION]
class FaceCustomerController extends Controller
{
    public function store(Request $request)
    {
        $data = $request->validate([
            'name' => 'required|string|max:255',
            'phone' => 'nullable|string|max:50',
            'discount_percent' => 'nullable|integer|min:0|max:100',
            'face_label' => 'required|string|max:100|regex:/^[A-Za-z0-9_-]+$/',
            'face_image_base64' => 'required|string|max:7000000',
            'face_embedding' => 'nullable|array', // Validate as array for JSON
            'consent_confirmed' => 'accepted',
        ]);

        $faceLabel = $data['face_label'];
        $discountPercent = $data['discount_percent'] ?? 0;
        $imagePath = $this->storeFaceImage($data['face_image_base64'], $faceLabel);

        $customer = Customer::updateOrCreate(
            ['face_label' => $faceLabel],
            [
                'name' => $data['name'],
                'phone' => $data['phone'] ?? null,
                'discount_percent' => $discountPercent,
                'is_member' => $discountPercent > 0,
                'face_image' => $imagePath,
                'face_embedding' => $data['face_embedding'] ?? null,
                'embedding_model' => 'Facenet512',
                'face_consent_at' => now(),
            ]
        );

        return response()->json([
            'success' => true,
            'message' => 'Customer berhasil disimpan.',
            'customer' => $customer,
        ]);
    }

    public function detectMember(Request $request)
    {
        $data = $request->validate([
            'face_label' => 'required|string|max:100',
            'score' => 'required|numeric|between:0,1',
            'liveness_passed' => 'required|boolean',
        ]);

        if (config('face.require_liveness') && !$data['liveness_passed']) {
            return response()->json([
                'success' => true,
                'found' => false,
                'message' => 'Liveness check gagal.',
            ]);
        }

        if ($data['score'] < config('face.minimum_score')) {
            return response()->json([
                'success' => true,
                'found' => false,
                'message' => 'Score pengenalan di bawah batas minimum.',
            ]);
        }

        $customer = Customer::where('face_label', $data['face_label'])
            ->where('is_member', true)
            ->first();

        if (!$customer) {
            return response()->json([
                'success' => true,
                'found' => false,
                'message' => 'Customer member tidak ditemukan.',
            ]);
        }

        $detectedAt = now();
        $detection = MemberDetection::create([
            'event_uuid' => (string) Str::uuid(),
            'customer_id' => $customer->id,
            'score' => $data['score'],
            'liveness_passed' => $data['liveness_passed'],
            'detected_at' => $detectedAt,
            'expires_at' => $detectedAt->copy()->addSeconds(config('face.detection_ttl_seconds')),
        ]);

        return response()->json([
            'success' => true,
            'found' => true,
            'message' => 'Customer member terdeteksi.',
            'detection' => $detection->only(['id', 'event_uuid', 'score', 'detected_at', 'expires_at']),
            'customer' => [
                'id' => $customer->id,
                'name' => $customer->name,
                'phone' => $customer->phone,
                'discount_percent' => $customer->discount_percent,
                'face_label' => $customer->face_label,
            ],
        ]);
    }

    public function showByFaceLabel(string $faceLabel)
    {
        $customer = Customer::where('face_label', $faceLabel)->firstOrFail();

        return response()->json([
            'success' => true,
            'customer' => $customer->only([
                'id', 'name', 'phone', 'face_label', 'discount_percent', 'is_member',
            ]),
        ]);
    }

    public function updateByFaceLabel(Request $request, string $faceLabel)
    {
        $customer = Customer::where('face_label', $faceLabel)->firstOrFail();
        $data = $request->validate([
            'name' => 'required|string|max:255',
            'phone' => 'nullable|string|max:50',
            'discount_percent' => 'required|integer|min:0|max:100',
        ]);

        // face_label remains immutable so the local face embeddings keep matching.
        $customer->update($data);

        return response()->json([
            'success' => true,
            'message' => 'Data member berhasil diperbarui.',
            'customer' => $customer->fresh()->only([
                'id', 'name', 'phone', 'face_label', 'discount_percent', 'is_member',
            ]),
        ]);
    }

    private function storeFaceImage(string $base64Image, string $faceLabel): string
    {
        $cleanImage = preg_replace('/^data:image\/[a-zA-Z]+;base64,/', '', $base64Image);
        $binaryImage = base64_decode($cleanImage);

        if ($binaryImage === false || strlen($binaryImage) > 5 * 1024 * 1024 || @getimagesizefromstring($binaryImage) === false) {
            abort(422, 'Format gambar base64 tidak valid.');
        }

        $path = 'private-faces/' . $faceLabel . '_' . Str::uuid() . '.jpg';
        Storage::disk('local')->put($path, $binaryImage);

        return $path;
    }
}
