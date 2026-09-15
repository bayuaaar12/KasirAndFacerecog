<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Customer extends Model
{
    use HasFactory;

    protected $guarded = [];

    protected $casts = [
        'is_member' => 'boolean',
        'face_consent_at' => 'datetime',
        'face_embedding' => 'array',
    ];
}
