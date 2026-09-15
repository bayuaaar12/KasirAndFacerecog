<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class MemberDetection extends Model
{
    use HasFactory;

    protected $guarded = [];

    protected $casts = [
        'detected_at' => 'datetime',
        'expires_at' => 'datetime',
        'applied_at' => 'datetime',
        'liveness_passed' => 'boolean',
        'score' => 'float',
    ];

    public function customer()
    {
        return $this->belongsTo(Customer::class);
    }

    public function transaksi()
    {
        return $this->belongsTo(Transaksi::class);
    }
}
