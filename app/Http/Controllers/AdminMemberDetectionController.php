<?php

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;
use App\Models\MemberDetection;

// [AI/ML INTEGRATION]
class AdminMemberDetectionController extends Controller
{
    public function latest(): JsonResponse
    {
        $detection = MemberDetection::query()
            ->with('customer:id,name,phone,discount_percent,face_label')
            ->whereNull('applied_at')
            ->where('expires_at', '>', now())
            ->latest('detected_at')
            ->first();

        $event = $detection ? [
            'id' => $detection->id,
            'event_uuid' => $detection->event_uuid,
            'customer_id' => $detection->customer_id,
            'name' => $detection->customer->name,
            'phone' => $detection->customer->phone,
            'discount_percent' => $detection->customer->discount_percent,
            'face_label' => $detection->customer->face_label,
            'score' => $detection->score,
            'detected_at' => $detection->detected_at->toDateTimeString(),
        ] : null;

        return response()->json([
            'success' => true,
            'event' => $event,
        ]);
    }
}
