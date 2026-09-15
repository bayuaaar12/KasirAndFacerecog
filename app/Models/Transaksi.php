<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Transaksi extends Model
{
    use HasFactory;

    protected $guarded = [];

    public function customer()
    {
        return $this->belongsTo(Customer::class);
    }

    public function details()
    {
        return $this->hasMany(TransaksiDetail::class);
    }

    public function recalculateTotal(): void
    {
        $subtotal = (int) $this->details()->sum('subtotal');
        $discountAmount = (int) round($subtotal * ((int) $this->discount_percent / 100));

        $this->update([
            'subtotal' => $subtotal,
            'discount_amount' => $discountAmount,
            'total' => max(0, $subtotal - $discountAmount),
        ]);
    }
}
