<?php

use App\Http\Controllers\Api\FaceCustomerController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::middleware(['api.key', 'throttle:api'])->group(function () {
    Route::post('/customers/register-face', [FaceCustomerController::class, 'store']);
    Route::post('/customers/detect-member', [FaceCustomerController::class, 'detectMember']);
    Route::get('/customers/{faceLabel}', [FaceCustomerController::class, 'showByFaceLabel'])
        ->where('faceLabel', '[A-Za-z0-9_-]+');
    Route::patch('/customers/{faceLabel}', [FaceCustomerController::class, 'updateByFaceLabel'])
        ->where('faceLabel', '[A-Za-z0-9_-]+');
});

Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});
